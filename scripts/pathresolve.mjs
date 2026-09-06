// pathresolve.mjs — 纯函数路径解析共享模块（无 CLI），镜像 scripts/pathresolve.py。
// 识别绝对/相对/~ 路径；is_windows 消歧 Windows 下 /x 为相对、nix 下 /x 为绝对。
import os from 'node:os';
import path from 'node:path';

function _detect_is_windows(is_windows) {
  return is_windows === undefined || is_windows === null ? process.platform === 'win32' : is_windows;
}

function isAbsolute(p, { is_windows } = {}) {
  if (_detect_is_windows(is_windows)) {
    return /^[A-Za-z]:[\\/]/.test(p) || p.startsWith('\\\\');
  }
  return p.startsWith('/');
}

function normalize(p) {
  let s = p.trim();
  if (s.length >= 2 && s[0] === s[s.length - 1] && (s[0] === "'" || s[0] === '"')) {
    s = s.slice(1, -1).trim();
  }
  if (s === '~') return os.homedir();
  if (s.startsWith('~/') || s.startsWith('~\\')) {
    return path.join(os.homedir(), s.slice(2));
  }
  return s;
}

function resolve(p, cwd, { is_windows } = {}) {
  const norm = normalize(p);
  const win = _detect_is_windows(is_windows);
  if (isAbsolute(norm, { is_windows: win })) {
    return path.resolve(norm);
  }
  return path.resolve(cwd, norm);
}

export { isAbsolute, normalize, resolve };
