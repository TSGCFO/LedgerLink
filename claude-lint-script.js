#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const ignore = require('ignore');

// Get git root directory
const gitRoot = execSync('git rev-parse --show-toplevel').toString().trim();
process.chdir(gitRoot);

// Create a prompt for Claude
const claudePrompt = `You are an advanced code reviewer and linter. Analyze the following code files and their relationships:

CHANGED FILES (Diffs vs. main branch):
\${DIFFS}

ALL PROJECT FILES (excluding .gitignore patterns):
\${FILES}

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

// Build list of all project files (respecting .gitignore)
function getAllProjectFiles() {
  try {
    // Read and parse .gitignore
    let ig = ignore();
    if (fs.existsSync('.gitignore')) {
      const gitignoreContent = fs.readFileSync('.gitignore', 'utf8');
      ig = ignore().add(gitignoreContent);
    }

    // Also add common files to ignore
    ig.add(['node_modules', '.git', 'dist', 'build']);

    // Get all files recursively
    function getAllFiles(dir, fileList = []) {
      const files = fs.readdirSync(dir);
      
      files.forEach(file => {
        const filePath = path.join(dir, file);
        const relativePath = path.relative(gitRoot, filePath);
        
        // Skip if ignored
        if (ig.ignores(relativePath)) return;
        
        if (fs.statSync(filePath).isDirectory()) {
          getAllFiles(filePath, fileList);
        } else {
          fileList.push(relativePath);
        }
      });
      
      return fileList;
    }

    const allFiles = getAllFiles(gitRoot);
    return allFiles.join('\n');
  } catch (error) {
    return `Error getting all files: ${error.message}`;
  }
}

// Analyze file dependencies (simplified - this could be more sophisticated)
function analyzeDependencies() {
  try {
    // This is a simple approach that works for JS/TS projects
    // For more complex projects, consider using tools like dependency-cruiser
    const allFiles = execSync('find . -type f -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" | grep -v "node_modules"').toString().trim().split('\n');
    
    const dependencies = {};
    
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
            deps.push(path.relative('.', resolvedPath));
          }
        } catch (e) {
          // Skip if we can't resolve
        }
      }
      
      if (deps.length > 0) {
        dependencies[file.substring(2)] = deps.map(d => d.startsWith('./') ? d.substring(2) : d);
      }
    }
    
    // Format dependencies
    let result = '';
    for (const [file, deps] of Object.entries(dependencies)) {
      result += `${file} depends on:\n`;
      deps.forEach(dep => {
        result += `  - ${dep}\n`;
      });
      result += '\n';
    }
    
    return result || "No dependencies detected.";
  } catch (error) {
    return `Error analyzing dependencies: ${error.message}`;
  }
}

// Main function
async function main() {
  console.log("Analyzing code with Claude...");
  
  // Get all required information
  const diffs = getGitDiffs();
  const allFiles = getAllProjectFiles();
  const dependencies = analyzeDependencies();
  
  // Build final prompt
  const finalPrompt = claudePrompt
    .replace('${DIFFS}', diffs)
    .replace('${FILES}', allFiles)
    .replace('${DEPENDENCIES}', dependencies);
  
  // Write prompt to a temp file to avoid command line length limitations
  fs.writeFileSync('.claude-temp-prompt.txt', finalPrompt);
  
  // Run Claude CLI with the prompt
  try {
    const result = execSync('claude -p "$(cat .claude-temp-prompt.txt)"').toString();
    console.log(result);
  } catch (error) {
    console.error("Error running Claude:", error.message);
  } finally {
    // Clean up
    fs.unlinkSync('.claude-temp-prompt.txt');
  }
}

main().catch(console.error);
