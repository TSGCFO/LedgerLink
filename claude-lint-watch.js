#!/usr/bin/env node

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const ignore = require('ignore');
const chokidar = require('chokidar');

// Get git root directory
const gitRoot = execSync('git rev-parse --show-toplevel').toString().trim();
process.chdir(gitRoot);

// Create a prompt for Claude
const claudePrompt = `You are an advanced code reviewer and linter. Analyze the following code files and their relationships:

CHANGED FILES (Diffs vs. main branch):
\${DIFFS}

RECENTLY MODIFIED FILES:
\${MODIFIED_FILES}

DEPENDENCIES BETWEEN FILES:
\${DEPENDENCIES}

Based on this information, identify:
1. Syntax errors and bugs in individual files
2. Inconsistencies or compatibility issues between dependent files
3. Performance concerns
4. Security vulnerabilities
5. Code style inconsistencies
6. Potential refactoring opportunities
7. Edge cases not handled
8. API mismatches between dependent modules
9. Typos and naming issues

For each issue found, format your response exactly as follows:
FILENAME:LINE_NUMBER
ISSUE: Brief description of the problem
FIX: Specific recommendation on how to fix it
SEVERITY: [Critical/High/Medium/Low]
RELATED_FILES: [List any files affected by or related to this issue]
---

Sort issues by severity, then by filename and line number. Only report actual issues - do not include compliments or other text.`;

// Get git diffs
function getGitDiffs() {
  try {
    // Get list of changed files
    const changedFiles = execSync('git diff --name-only origin/main').toString().trim().split('\n');
    if (!changedFiles[0]) return "No changed files detected.";

    let diffs = "";
    for (const file of changedFiles) {
      if (!file || !fs.existsSync(file)) continue;
      diffs += `--- ${file} ---\n`;
      diffs += execSync(`git diff origin/main -- "${file}"`).toString().trim() + "\n\n";
    }
    return diffs || "No meaningful diffs detected.";
  } catch (error) {
    return `Error getting diffs: ${error.message}`;
  }
}

// Analyze file content for specific modified files
function getModifiedFilesContent(modifiedFiles) {
  try {
    let content = "";
    for (const file of modifiedFiles) {
      if (!fs.existsSync(file)) continue;
      content += `--- ${file} ---\n`;
      content += fs.readFileSync(file, 'utf8') + "\n\n";
    }
    return content || "No modified files content to analyze.";
  } catch (error) {
    return `Error getting modified files content: ${error.message}`;
  }
}

// Build dependency graph and get affected files
function analyzeDependencies(modifiedFiles = []) {
  try {
    // This is a simple approach that works for JS/TS projects
    const allFiles = execSync('find . -type f -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" | grep -v "node_modules"').toString().trim().split('\n');
    
    const dependencies = {};
    const reverseDependencies = {};
    
    // Build forward and reverse dependency mappings
    for (const file of allFiles) {
      if (!file) continue;
      
      const content = fs.readFileSync(file, 'utf8');
      
      // Find imports (this is a simple regex that might miss some patterns)
      const importRegex = /(?:import|require)\s*\(?['"]([^'"]+)['"]\)?/g;
      let match;
      const deps = [];
      
      while ((match = importRegex.exec(content)) !== null) {
        const importPath = match[1];
        if (!importPath.startsWith('.')) continue; // Skip external packages
        
        // Resolve relative path
        let resolvedPath;
        try {
          // Try various extensions
          const extensions = ['.js', '.jsx', '.ts', '.tsx', '.json'];
          const dir = path.dirname(file);
          
          for (const ext of extensions) {
            const testPath = path.join(dir, importPath + ext);
            if (fs.existsSync(testPath)) {
              resolvedPath = testPath;
              break;
            }
            
            // Try with /index
            const indexPath = path.join(dir, importPath, 'index' + ext);
            if (fs.existsSync(indexPath)) {
              resolvedPath = indexPath;
              break;
            }
          }
          
          if (resolvedPath) {
            const relPath = path.relative('.', resolvedPath);
            deps.push(relPath);
            
            // Build reverse dependency map
            if (!reverseDependencies[relPath]) {
              reverseDependencies[relPath] = [];
            }
            reverseDependencies[relPath].push(file.substring(2));
          }
        } catch (e) {
          // Skip if we can't resolve
        }
      }
      
      if (deps.length > 0) {
        dependencies[file.substring(2)] = deps.map(d => d.startsWith('./') ? d.substring(2) : d);
      }
    }
    
    // If we have modified files, find all affected files (dependencies and dependents)
    let affectedFiles = [...modifiedFiles];
    if (modifiedFiles.length > 0) {
      // Find all files affected by modified files (files that depend on our changes)
      for (const modifiedFile of modifiedFiles) {
        const relModifiedFile = modifiedFile.startsWith('./') ? modifiedFile.substring(2) : modifiedFile;
        
        // Add files that depend on this file
        if (reverseDependencies[relModifiedFile]) {
          affectedFiles = [...affectedFiles, ...reverseDependencies[relModifiedFile]];
        }
        
        // Add files this file depends on
        if (dependencies[relModifiedFile]) {
          affectedFiles = [...affectedFiles, ...dependencies[relModifiedFile]];
        }
      }
      
      // Remove duplicates
      affectedFiles = [...new Set(affectedFiles)];
    }
    
    // Format dependencies with highlighting for affected files
    let result = '';
    for (const [file, deps] of Object.entries(dependencies)) {
      const isAffected = affectedFiles.includes(file);
      result += `${isAffected ? '[AFFECTED] ' : ''}${file} depends on:\n`;
      deps.forEach(dep => {
        const isDepAffected = affectedFiles.includes(dep);
        result += `  - ${isDepAffected ? '[AFFECTED] ' : ''}${dep}\n`;
      });
      result += '\n';
    }
    
    // Return both the dependency analysis and the list of affected files
    return {
      analysis: result || "No dependencies detected.",
      affectedFiles
    };
  } catch (error) {
    return {
      analysis: `Error analyzing dependencies: ${error.message}`,
      affectedFiles: modifiedFiles
    };
  }
}

// Setup gitignore patterns
function getIgnorer() {
  let ig = ignore();
  if (fs.existsSync('.gitignore')) {
    const gitignoreContent = fs.readFileSync('.gitignore', 'utf8');
    ig = ignore().add(gitignoreContent);
  }
  // Also add common files to ignore
  ig.add(['node_modules', '.git', 'dist', 'build', '.claude-temp-prompt.txt']);
  return ig;
}

// Run Claude analysis
async function runAnalysis(modifiedFiles = []) {
  console.log("Analyzing code with Claude...");
  
  // Get all required information
  const diffs = getGitDiffs();
  const { analysis: dependencies, affectedFiles } = analyzeDependencies(modifiedFiles);
  const modifiedFilesContent = getModifiedFilesContent(affectedFiles);
  
  // Build final prompt
  const finalPrompt = claudePrompt
    .replace('${DIFFS}', diffs)
    .replace('${MODIFIED_FILES}', modifiedFilesContent)
    .replace('${DEPENDENCIES}', dependencies);
  
  // Write prompt to a temp file to avoid command line length limitations
  fs.writeFileSync('.claude-temp-prompt.txt', finalPrompt);
  
  // Run Claude CLI with the prompt
  try {
    console.log(`Running analysis on ${modifiedFiles.length} modified files and ${affectedFiles.length - modifiedFiles.length} related files...`);
    const result = execSync('claude -p "$(cat .claude-temp-prompt.txt)"').toString();
    
    // Display results with timestamp
    const timestamp = new Date().toLocaleTimeString();
    console.log(`\n=== CLAUDE ANALYSIS RESULTS (${timestamp}) ===\n`);
    console.log(result);
    console.log('\n=== END OF ANALYSIS ===\n');
  } catch (error) {
    console.error("Error running Claude:", error.message);
  } finally {
    // Clean up
    fs.unlinkSync('.claude-temp-prompt.txt');
  }
}

// Main function for manual execution
async function main() {
  await runAnalysis([]);
}

// Watcher mode
function watchMode() {
  const ig = getIgnorer();
  console.log("Starting Claude code watcher...");
  console.log("Monitoring for file changes (press Ctrl+C to exit)...");
  
  // Use chokidar to watch file changes
  const watcher = chokidar.watch('.', {
    ignored: path => {
      const relativePath = path.startsWith('./') ? path.substring(2) : path;
      return ig.ignores(relativePath) || /^\.(git|vscode|idea)/.test(relativePath);
    },
    persistent: true,
    ignoreInitial: true
  });
  
  let debounceTimer;
  let pendingChanges = new Set();
  
  // When files change, trigger analysis
  watcher.on('all', (event, filePath) => {
    if (event === 'add' || event === 'change' || event === 'unlink') {
      pendingChanges.add(filePath);
      
      // Debounce to avoid multiple rapid analyses
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const modifiedFiles = Array.from(pendingChanges);
        console.log(`\nDetected ${modifiedFiles.length} file changes. Running analysis...`);
        runAnalysis(modifiedFiles);
        pendingChanges.clear();
      }, 2000); // Wait 2 seconds after the last change
    }
  });
  
  console.log("Watching for file changes...");
}

// Check if we're in watch mode
if (process.argv.includes('--watch') || process.argv.includes('-w')) {
  watchMode();
} else {
  main().catch(console.error);
}
