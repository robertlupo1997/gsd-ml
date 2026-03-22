#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

// Colors
const cyan = '\x1b[36m';
const green = '\x1b[32m';
const yellow = '\x1b[33m';
const dim = '\x1b[2m';
const reset = '\x1b[0m';

// Get version from package.json
const pkg = require('../package.json');

const banner = '\n' +
  cyan + '   ██████╗ ███████╗██████╗       ███╗   ███╗██╗\n' +
  '  ██╔════╝ ██╔════╝██╔══██╗      ████╗ ████║██║\n' +
  '  ██║  ███╗███████╗██║  ██║█████╗██╔████╔██║██║\n' +
  '  ██║   ██║╚════██║██║  ██║╚════╝██║╚██╔╝██║██║\n' +
  '  ╚██████╔╝███████║██████╔╝      ██║ ╚═╝ ██║███████╗\n' +
  '   ╚═════╝ ╚══════╝╚═════╝       ╚═╝     ╚═╝╚══════╝' + reset + '\n' +
  '\n' +
  '  GSD-ML ' + dim + 'v' + pkg.version + reset + '\n' +
  '  Claude Code native autonomous ML research tool.\n';

console.log(banner);

// Source directory (package root)
const src = path.join(__dirname, '..');

// Target directory: always ~/.claude/ (global install to Claude Code config)
const homeDir = os.homedir();
const claudeDir = path.join(homeDir, '.claude');

// Path prefix for file references in markdown content
const pathPrefix = claudeDir.replace(/\\/g, '/') + '/';

/**
 * Convert absolute path prefix to $HOME-relative form for portable paths.
 */
function toHomePrefix(prefix) {
  const home = homeDir.replace(/\\/g, '/');
  const normalized = prefix.replace(/\\/g, '/');
  if (normalized.startsWith(home)) {
    return '$HOME' + normalized.slice(home.length);
  }
  return normalized;
}

/**
 * Recursively copy a directory, replacing path references in .md files.
 * Replaces ~/.claude/ with the actual install path prefix.
 */
function copyWithPathReplacement(srcDir, destDir) {
  // Clean install: remove existing destination to prevent orphaned files
  if (fs.existsSync(destDir)) {
    fs.rmSync(destDir, { recursive: true });
  }
  fs.mkdirSync(destDir, { recursive: true });

  const entries = fs.readdirSync(srcDir, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(srcDir, entry.name);
    const destPath = path.join(destDir, entry.name);

    if (entry.isDirectory()) {
      copyWithPathReplacement(srcPath, destPath);
    } else if (entry.name.endsWith('.md')) {
      // Replace path references in markdown files
      let content = fs.readFileSync(srcPath, 'utf8');
      const globalClaudeRegex = /~\/\.claude\//g;
      const globalClaudeHomeRegex = /\$HOME\/\.claude\//g;
      content = content.replace(globalClaudeRegex, pathPrefix);
      content = content.replace(globalClaudeHomeRegex, toHomePrefix(pathPrefix));
      fs.writeFileSync(destPath, content);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

/**
 * Verify a directory was installed and contains files.
 */
function verifyInstalled(dir, label) {
  if (!fs.existsSync(dir)) {
    console.log(`  ${yellow}!${reset} Missing: ${label}`);
    return false;
  }
  const files = fs.readdirSync(dir);
  if (files.length === 0) {
    console.log(`  ${yellow}!${reset} Empty: ${label}`);
    return false;
  }
  return true;
}

// Track installation failures
const failures = [];

// 1. Install commands/gsd-ml/ to ~/.claude/commands/gsd-ml/
const commandsSrc = path.join(src, 'commands', 'gsd-ml');
const commandsDest = path.join(claudeDir, 'commands', 'gsd-ml');
fs.mkdirSync(path.join(claudeDir, 'commands'), { recursive: true });
copyWithPathReplacement(commandsSrc, commandsDest);
if (verifyInstalled(commandsDest, 'commands/gsd-ml')) {
  console.log(`  ${green}+${reset} Installed commands/gsd-ml`);
} else {
  failures.push('commands/gsd-ml');
}

// 2. Install gsd-ml/ to ~/.claude/gsd-ml/
const skillSrc = path.join(src, 'gsd-ml');
const skillDest = path.join(claudeDir, 'gsd-ml');
copyWithPathReplacement(skillSrc, skillDest);
if (verifyInstalled(skillDest, 'gsd-ml')) {
  console.log(`  ${green}+${reset} Installed gsd-ml`);
} else {
  failures.push('gsd-ml');
}

// 3. Validate Python package
console.log('');
try {
  execSync('python3 -c "import gsd_ml"', { stdio: 'pipe' });
  console.log(`  ${green}+${reset} Python package gsd_ml found`);
} catch {
  console.log(`  ${yellow}!${reset} Python package gsd_ml not found`);
  console.log(`    Install with: ${cyan}pip install gsd-ml${reset}`);
  console.log(`    ${dim}(ML workflows require the Python utilities)${reset}`);
}

// Summary
console.log('');
if (failures.length === 0) {
  console.log(`  ${green}Installation complete!${reset}`);
  console.log(`  ${dim}Skills installed to ${claudeDir.replace(homeDir, '~')}/commands/gsd-ml/${reset}`);
  console.log(`  ${dim}Workflows installed to ${claudeDir.replace(homeDir, '~')}/gsd-ml/${reset}`);
  console.log('');
  console.log(`  ${dim}Use /gsd:ml in Claude Code to run an ML experiment.${reset}`);
} else {
  console.log(`  ${yellow}Installation completed with errors:${reset}`);
  for (const f of failures) {
    console.log(`    ${yellow}-${reset} Failed to install: ${f}`);
  }
}
console.log('');
