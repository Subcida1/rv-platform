/* Where a flatpak Chrome actually puts --user-data-dir, and how to delete it.
 *
 * THE BUG THIS EXISTS FOR (2026-10-04). check-a11y.mjs and check-diagram-fit.mjs
 * both ran this, verbatim:
 *
 *     const PROFILE = `/tmp/cdp-a11y-${process.pid}`;
 *     fs.rmSync(PROFILE, { recursive: true, force: true });   // cleanup, on exit
 *
 * and both leaked every profile they ever made. Flatpak gives the app a PRIVATE
 * /tmp, so `--user-data-dir=/tmp/cdp-a11y-1234` is written to
 *
 *     $XDG_RUNTIME_DIR/.flatpak/com.google.Chrome/tmp/cdp-a11y-1234
 *
 * on the host, while `rmSync('/tmp/cdp-a11y-1234')` deletes the host path --
 * which Chrome never touched. `force: true` swallowed the difference, so the
 * cleanup reported success every time and removed nothing.
 *
 * Measured that evening: 28 stale profiles, 1.6 GB, in a 1.6 GB tmpfs, and the
 * XDG runtime dir at 100%. The symptom is not "some profiles left behind" --
 * it is that NOTHING FLATPAK CAN START, with the error
 *
 *     error: fallocate: No space left on device
 *
 * which reads as "the disk is full" while `df -h /` shows 178 GB free. The one
 * number that would have named it is `df -h $XDG_RUNTIME_DIR`.
 *
 * So the rule: the string handed to Chrome is the sandbox's view, the path
 * handed to rmSync has to be the host's, and they are not the same string.
 */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

/** The host directory that a flatpak app sees as /tmp. null when unset. */
export function sandboxTmp(appId = 'com.google.Chrome') {
  const rt = process.env.XDG_RUNTIME_DIR || defaultRuntimeDir();
  if (!rt) return null;
  const p = path.join(rt, '.flatpak', appId, 'tmp');
  return fs.existsSync(p) ? p : null;
}

/** XDG_RUNTIME_DIR's conventional value when a minimal environment (cron) omits it.
 *  Without this the sweep cleans host /tmp and misses the directory flatpak Chrome actually
 *  writes to -- the exact place the 1.6 GB of orphaned profiles lived. Cron's environment has
 *  no XDG_RUNTIME_DIR, so falling back to /run/user/<uid> is the difference between the sweep
 *  working under cron and the sweep being blind under cron. */
export function defaultRuntimeDir() {
  if (process.env.XDG_RUNTIME_DIR) return process.env.XDG_RUNTIME_DIR;
  if (typeof process.getuid === 'function' && fs.existsSync(`/run/user/${process.getuid()}`))
    return `/run/user/${process.getuid()}`;
  return null;
}

/** Every host path a `--user-data-dir=/tmp/<leaf>` actually writes to. */
export function profileOnDisk(leaf) {
  const out = [path.join('/tmp', leaf)];
  const sb = sandboxTmp();
  if (sb) out.push(path.join(sb, leaf));
  return out;
}

/** Delete a profile by the same leaf name that was passed to Chrome. */
export function removeProfile(leaf) {
  for (const p of profileOnDisk(leaf)) fs.rmSync(p, { recursive: true, force: true });
}

/**
 * How full the runtime tmpfs is, 0..1. Worth printing when it is high: it is
 * the only number that explains "No space left on device" on a machine with a
 * nearly empty disk.
 */
export function runtimeFullness() {
  const rt = defaultRuntimeDir();
  if (!rt) return null;
  try {
    const s = fs.statfsSync(rt);
    return 1 - s.bavail / s.blocks;
  } catch { return null; }
}

/** Say it out loud when the runtime dir is close to the ceiling. */
export function warnIfRuntimeFull(where = 'headless Chrome') {
  const f = runtimeFullness();
  if (f === null || f < 0.85) return;
  console.error(`warning: $XDG_RUNTIME_DIR is ${(f * 100).toFixed(0)}% full. `
    + `${where} will fail with "fallocate: No space left on device" while df shows a nearly empty disk.\n`
    + `         inspect: du -sh $XDG_RUNTIME_DIR/.flatpak/*/tmp/* | sort -rh | head`);
}

/* THE TEARDOWN IS NOT ENOUGH ON ITS OWN (2026-11-26).

 * Every browser check deletes its own profile in a cleanup() wired to process.on('exit'),
 * and that works while the check runs to completion. It does NOT survive the two ways a
 * gate actually dies:

 *   1. SIGKILL/SIGTERM. process.on('exit') does not fire for a signal. cron's flock, a
 *      container stop, or a cancelled run kills node outright and cleanup() never runs.

 *   2. The reparented sandbox. The check spawns `flatpak run com.google.Chrome`, which
 *      becomes the process-group leader; the real Chrome runs inside bubblewrap and is
 *      reparented to `systemd --user`, OUTSIDE that group. `process.kill(-pid)` reaches
 *      flatpak and misses bwrap + /app/extra/chrome, which keep the profile dir open. The
 *      rmSync then fails on a busy tree and `force: true` swallows it.

 * Both leave a live headless Chrome holding a `cdp-*` profile that survives every later
 * cleanup -- measured on 2026-11-25: four such orphans, 1.1 GB, in a 1.6 GB tmpfs. The
 * per-check fix cannot see this; only a sweep that runs AFTER the stage, from outside it,
 * can. So the gate calls sweepOrphanProfiles() once at the end, in the same shell that
 * would otherwise exit -- it finds any process still holding a cdp-* profile and removes
 * every cdp-* profile left behind, regardless of which stage died and how.
 */
const CDP_LEAF = /(?:^|[\\/])cdp-[A-Za-z0-9._-]+/;

/** Every cdp-* profile dir currently on disk, host /tmp and the flatpak sandbox alike. */
export function orphanProfileDirs() {
  const out = [];
  const dirs = [path.join('/tmp')];
  const sb = sandboxTmp();
  if (sb) dirs.push(sb);
  for (const d of dirs) {
    let entries = [];
    try { entries = fs.readdirSync(d); } catch { continue; }
    for (const e of entries) if (e.startsWith('cdp-')) out.push(path.join(d, e));
  }
  return out;
}

/** PIDs holding any open file inside `dir`, via `lsof +D`. Precise: argv is never consulted.
 *  `fuser <dir>` does NOT work here -- it matches only the directory inode, and a chrome child
 *  holds files *inside* the profile, not the dir itself. `lsof +D` walks the tree and names
 *  every holder, which is what a sweep has to kill. */
function holdersOf(dir) {
  try {
    const out = execFileSync('lsof', ['-t', '+D', dir], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    return [...new Set((out.match(/\d+/g) || []).map(Number))].filter((p) => p !== process.pid);
  } catch (e) {
    const txt = String(e.stdout || '');
    return [...new Set((txt.match(/\d+/g) || []).map(Number))].filter((p) => p !== process.pid);
  }
}

/** SIGKILL whatever holds a cdp-* profile open, then delete every cdp-* profile dir, then
 *  remove stale flatpak socket files. */
export function sweepOrphanProfiles({ quiet = false } = {}) {
  const killed = [];
  const removed = [];
  for (const dir of orphanProfileDirs()) {
    // lsof finds the exact processes with a file open in the profile, INCLUDING the chrome
    // children whose argv never carried --user-data-dir. No argv pattern, so it cannot kill a
    // caller that merely names a profile, and cannot miss a child that a leaf-match would.
    for (const pid of holdersOf(dir)) {
      try { process.kill(pid, 'SIGKILL'); killed.push(pid); } catch {}
    }
    try { fs.rmSync(dir, { recursive: true, force: true }); removed.push(dir); } catch {}
  }
  const sockets = sweepStaleSockets();
  if (!quiet && (killed.length || removed.length || sockets))
    console.error(`swept ${killed.length} orphan chrome process(es)` +
      (removed.length ? `, removed ${removed.length} cdp-* profile dir(s)` : '') +
      (sockets ? `, cleared ${sockets} stale flatpak socket file(s)` : ''));
  return { killed, removed, sockets };
}

/** Flatpak Chrome leaves one singleton dir (`com.google.Chrome.<ID>`) per launch, holding only
 *  SingletonCookie/SingletonLock symlinks, plus one socket file per launch, in its sandbox tmp.
 *  Nothing ever removes them: measured 2026-11-26, 308 dirs plus ~570 files and 57 MB, dating
 *  back a day. They are not a cdp- profile, so the profile sweep above never sees them. Remove
 *  ONLY entries with zero open references -- a live instance's own dir and socket must stay, and
 *  a running desktop Chrome's must stay too. Returns how many were removed. */
export function sweepStaleSockets() {
  const sb = sandboxTmp();
  if (!sb) return 0;
  let entries = [];
  try { entries = fs.readdirSync(sb); } catch { return 0; }
  let n = 0;
  for (const e of entries) {
    if (!e.startsWith('com.google.Chrome.') && !e.startsWith('.com.google.Chrome.')) continue;
    const full = path.join(sb, e);
    const held = holdersOf(full);           // lsof +D walks a dir; for a file it names the holder
    // For a bare file, holdersOf's +D flag is wrong, so check directly too.
    let live = held.length > 0;
    if (!live) {
      try {
        const out = execFileSync('lsof', ['-t', full], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
        live = out.trim().length > 0;
      } catch { /* nothing holds it -- removable */ }
    }
    if (live) continue;                     // a live chrome owns it; leave it alone
    // Never remove anything substantial: a real profile has content. These singleton dirs hold
    // only the Singleton* symlinks, so cap the whole thing at a few KB as a second guard beyond
    // the liveness check -- if it is bigger, it is not ours to delete.
    try {
      const st = fs.lstatSync(full);
      if (st.isDirectory()) {
        const inner = fs.readdirSync(full);
        if (inner.length > 8 || inner.some((f) => !/^Singleton/.test(f))) continue;
      }
    } catch { continue; }
    try { fs.rmSync(full, { recursive: true, force: true }); n += 1; } catch {}
  }
  return n;
}

// Runnable as a CLI so ci.sh can sweep without importing:  node scripts/lib/chrome-profile.mjs --sweep
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
    && process.argv.includes('--sweep')) {
  const { killed, removed, sockets } = sweepOrphanProfiles();
  if (!killed.length && !removed.length && !sockets) console.log('no orphan chrome profiles to sweep');
  process.exit(0);
}
