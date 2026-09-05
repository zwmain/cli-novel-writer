#!/usr/bin/env node
// write_file.mjs — 写入文件，父目录缺失时默认递归创建（无需开关）。
//
// 用法: write_file.mjs <路径> <内容>
// 退出码: 0=写入成功  1=写入失败  2=用法错误  3=环境/IO 错误

import { resolve } from './pathresolve.mjs';
import fs from 'node:fs';
import path from 'node:path';

const USAGE = '用法: write_file.mjs <路径> <内容>';

function _print_usage(file) {
  // 与 py 版逐字一致：说明 + 用法。
  file.write('写入文件（父目录缺失时递归创建；内容可含多行，不做转义）\n' + USAGE + '\n');
}

function main(argv) {
  // node 的 process.argv 以 argv[2] 起为用户参数，取 [2:] 与 py 的 argv[1:] 对齐。
  const args = argv.slice(2);
  if (args.length !== 2) {
    // 与 py 相同：len==2 且为 -h/--help → 帮助 0；len==3 时把 argv[3] 当内容（含 --help）先写入。
    if (args.length === 1 && (args[0] === '-h' || args[0] === '--help')) {
      _print_usage(process.stdout);
      return 0;
    }
    process.stderr.write(USAGE + '\n');
    return 2;
  }
  const [pathArg, content] = args;
  let cwd;
  try {
    cwd = process.cwd();
  } catch (exc) {
    process.stderr.write(`无法获取当前工作目录: ${exc}\n`);
    return 3;
  }
  let abs_path;
  try {
    abs_path = resolve(pathArg, cwd);
  } catch (exc) {
    process.stderr.write(`无法解析路径 ${pathArg}: ${exc}\n`);
    return 3;
  }
  try {
    fs.mkdirSync(path.dirname(abs_path), { recursive: true });
    fs.writeFileSync(abs_path, content, 'utf-8');
  } catch (exc) {
    process.stderr.write(`无法写入文件 ${abs_path}: ${exc}\n`);
    return 1;
  }
  process.stdout.write(abs_path + '\n');
  return 0;
}

process.exitCode = main(process.argv);
