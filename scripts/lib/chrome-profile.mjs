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

/** The host directory that a flatpak app sees as /tmp. null when unset. */
export function sandboxTmp(appId = 'com.google.Chrome') {
  const rt = process.env.XDG_RUNTIME_DIR;
  if (!rt) return null;
  const p = path.join(rt, '.flatpak', appId, 'tmp');
  return fs.existsSync(p) ? p : null;
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
  const rt = process.env.XDG_RUNTIME_DIR;
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
