#!/usr/bin/env node
// check_dir.mjs — 检查目录是否存在，可选一键创建（纯检查 / 检查+创建）。
//
// 用法: check_dir.mjs <路径> [--create]
// 退出码: 0=存在/创建成功  1=不存在/无法创建  2=用法错误  3=环境/IO 错误

import { resolve } from './pathresolve.mjs';
import fs from 'node:fs';

const USAGE = '用法: check_dir.mjs <路径> [--create]';

function _print_usage(file) {
  // 与 py 版逐字一致：说明 + 用法。
  file.write('检查目录是否存在，可选一键创建（嵌套路径一并创建）\n' + USAGE + '\n');
}

function main(argv) {
  // node 的 process.argv 以 argv[2] 起为用户参数，取 [2:] 与 py 的 argv[1:] 对齐。
  const args = argv.slice(2);
  if (args.length < 1) {
    process.stderr.write(USAGE + '\n');
    return 2;
  }
  if (args[0] === '-h' || args[0] === '--help') {
    _print_usage(process.stdout);
    return 0;
  }
  const create = args[0] === '--create';
  const i = create ? 1 : 0;
  if (i >= args.length) {
    process.stderr.write(USAGE + '\n');
    return 2;
  }
  // 未知 `-` 前缀参数（非 --create/-h/--help）→ 用法错误。
  if (args[i].startsWith('-')) {
    process.stderr.write(USAGE + '\n');
    return 2;
  }
  // 超出预期（--create 标志后恰 1 个路径，或无标志恰 1 个路径）的尾随参数 → 用法错误。
  if (i + 1 < args.length) {
    process.stderr.write(USAGE + '\n');
    return 2;
  }
  const path = args[i];
  let cwd;
  try {
    cwd = process.cwd();
  } catch (exc) {
    process.stderr.write(`无法获取当前工作目录: ${exc}\n`);
    return 3;
  }
  let abs_path;
  try {
    abs_path = resolve(path, cwd);
  } catch (exc) {
    process.stderr.write(`无法解析路径 ${path}: ${exc}\n`);
    return 3;
  }
  if (!create) {
    // 优先用 statSync+isDirectory 判断，避免 existsSync 对「文件」也返回 true 的边界。
    let exists = false;
    try {
      exists = fs.statSync(abs_path).isDirectory();
    } catch {
      exists = false;
    }
    if (!exists) {
      process.stderr.write(`目录不存在: ${abs_path}\n`);
      return 1;
    }
    process.stdout.write(abs_path + '\n');
    return 0;
  }
  try {
    fs.mkdirSync(abs_path, { recursive: true });
  } catch (exc) {
    process.stderr.write(`无法创建目录 ${abs_path}: ${exc}\n`);
    return 1;
  }
  process.stdout.write(abs_path + '\n');
  return 0;
}

process.exitCode = main(process.argv);
