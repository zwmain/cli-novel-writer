#!/usr/bin/env node
// count_cjk.mjs — 统计文本文件中的中文字符数（正则 [一-龥]，标点/空白/拉丁不计）。
//
// 用法: count_cjk.mjs <文件> [--min N] [--max M]
// 退出码: 0=通过  1=未达区间  2=用法错误  3=文件不可读

import fs from 'node:fs';

const CJK_RE = /[一-龥]/g;   // [一-龥]，g 以便 matchAll/count
const MIN_WORDS = 2000;      // 每章期望下限（中文字符）
const MAX_WORDS = 4000;      // 每章期望上限（中文字符）

function count_cjk(text) {
  // 返回 text 中的中文字符数量（标点/空白/拉丁不计）。
  const m = text.match(CJK_RE);
  return m ? m.length : 0;
}

function _check_range(count, lo, hi) {
  // count 是否落在 [lo, hi]（含边界）。
  return lo <= count && count <= hi;
}

function main(argv) {
  // node 的 process.argv 以 argv[2] 起为用户参数，取 [2:] 与 py 的 argv[1:] 对齐。
  const args = argv.slice(2);
  if (args.length < 1) {
    process.stderr.write('用法: count_cjk.mjs <文件> [--min N] [--max M]\n');
    return 2;
  }
  if (args[0] === '-h' || args[0] === '--help') {
    process.stderr.write(
      '统计文件中的中文字符数（标点/空白/拉丁不计）\n' +
      '用法: count_cjk.mjs <文件> [--min N] [--max M]\n',
    );
    return 0;
  }
  let lo = MIN_WORDS;
  let hi = MAX_WORDS;
  let i = 1;
  while (i < args.length) {
    if (args[i] === '--min' && i + 1 < args.length) {
      lo = Number(args[i + 1]);
      i += 2;
    } else if (args[i] === '--max' && i + 1 < args.length) {
      hi = Number(args[i + 1]);
      i += 2;
    } else {
      process.stderr.write(`未知参数: ${args[i]}\n`);
      return 2;
    }
  }
  let count;
  try {
    count = count_cjk(fs.readFileSync(args[0], 'utf-8'));
  } catch (exc) {
    process.stderr.write(`无法读取文件 ${args[0]}: ${exc.message}\n`);
    return 3;
  }
  const ok = _check_range(count, lo, hi);
  process.stdout.write(`${count} 中文字符\n`);
  process.stdout.write(ok ? 'PASS\n' : `FAIL: 不在 [${lo}, ${hi}] 区间\n`);
  return ok ? 0 : 1;
}

process.exitCode = main(process.argv);
