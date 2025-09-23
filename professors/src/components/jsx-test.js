const { parse } = require('@babel/parser');
const fs = require('fs');

try {
  const code = fs.readFileSync('ComprehensiveTeacherSearch.jsx', 'utf8');
  const ast = parse(code, {
    sourceType: 'module',
    plugins: ['jsx', 'typescript']
  });
  console.log('JSX parsing successful - no syntax errors found');
} catch (error) {
  console.log('JSX syntax error:', error.message);
  console.log('Location:', error.loc);
}