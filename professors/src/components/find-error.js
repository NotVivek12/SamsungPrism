const fs = require('fs');

const code = fs.readFileSync('ComprehensiveTeacherSearch.jsx', 'utf8');
const lines = code.split('\n');

// Find line 1197 (1-indexed)
const lineIndex = 1197 - 1;
const errorLine = lines[lineIndex];

console.log(`Line ${1197}: "${errorLine}"`);
console.log('Character at column 4:', errorLine ? errorLine[3] : 'undefined');

// Show context around the error
const start = Math.max(0, lineIndex - 5);
const end = Math.min(lines.length, lineIndex + 5);

console.log('\nContext around error:');
for (let i = start; i < end; i++) {
  const lineNum = i + 1;
  const prefix = lineNum === 1197 ? '>>> ' : '    ';
  console.log(`${prefix}${lineNum}: ${lines[i]}`);
}