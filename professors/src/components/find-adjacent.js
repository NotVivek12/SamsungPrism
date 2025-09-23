const fs = require('fs');

const code = fs.readFileSync('ComprehensiveTeacherSearch.jsx', 'utf8');

// Look for patterns that might cause adjacent JSX elements
const patterns = [
  // JSX expressions followed directly by another JSX element
  /\}\s*<\w+/g,
  // Closing JSX followed by opening JSX without proper wrapper
  />\s*<\w+[^>]*>/g,
  // Conditional rendering that might return multiple elements
  /\?\s*\(<[^>]+>[\s\S]*?<\/[^>]+>\s*\)\s*:\s*\(<[^>]+>/g
];

patterns.forEach((pattern, index) => {
  const matches = [...code.matchAll(pattern)];
  if (matches.length > 0) {
    console.log(`Pattern ${index + 1} matches found:`);
    matches.forEach(match => {
      const startIndex = match.index;
      const lines = code.substring(0, startIndex).split('\n');
      const lineNumber = lines.length;
      console.log(`  Line ${lineNumber}: "${match[0].trim()}"`);
    });
    console.log('');
  }
});

// Also check for potential React fragment issues
const fragmentPattern = /<>\s*[\s\S]*?<\/>/g;
const fragmentMatches = [...code.matchAll(fragmentPattern)];
if (fragmentMatches.length > 0) {
  console.log('React fragments found:');
  fragmentMatches.forEach(match => {
    const startIndex = match.index;
    const lines = code.substring(0, startIndex).split('\n');
    const lineNumber = lines.length;
    console.log(`  Line ${lineNumber}: Fragment`);
  });
}