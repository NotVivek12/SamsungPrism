const fs = require('fs');

const code = fs.readFileSync('ComprehensiveTeacherSearch.jsx', 'utf8');
const lines = code.split('\n');

// Find line 1198 (1-indexed)
const lineIndex = 1198 - 1;
const errorLine = lines[lineIndex];

console.log(`Line ${1198}: "${errorLine}"`);

// Show context around the error
const start = Math.max(0, lineIndex - 10);
const end = Math.min(lines.length, lineIndex + 10);

console.log('\nContext around error:');
for (let i = start; i < end; i++) {
  const lineNum = i + 1;
  const prefix = lineNum === 1198 ? '>>> ' : '    ';
  console.log(`${prefix}${lineNum}: ${lines[i]}`);
}