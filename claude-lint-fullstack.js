#!/usr/bin/env node
/**
 * LedgerLink Fullstack Linter
 * 
 * This script provides comprehensive linting for Django/React fullstack applications
 * using Claude AI. It analyzes code across the stack to find issues like:
 * 
 * - API endpoint mismatches between Django URLs and React API calls
 * - Data structure inconsistencies between Django models and React state/props
 * - Security vulnerabilities and performance concerns
 * - Code style and logic issues
 * 
 * Usage:
 *   npm run lint          - Run a full analysis once
 *   npm run lint:watch    - Run in watch mode, analyzing files as they change
 *   npm run lint:claude   - Run raw Claude analysis
 * 
 * The script examines:
 * - Django models and URL configurations
 * - React components and API calls
 * - Dependencies between files
 * - Git diffs against main branch
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const ignore = require('ignore');
const chokidar = require('chokidar');

// Get project root directory (try git first, fall back to current directory)
const GIT_PATH = '"C:\\Program Files\\GitHub CLI\\gh.exe"';
let gitRoot;
try {
  gitRoot = execSync(`${GIT_PATH} rev-parse --show-toplevel`).toString().trim();
  process.chdir(gitRoot);
} catch (error) {
  console.log("Git not detected, using current directory as project root");
  gitRoot = process.cwd();
}

// Create a prompt for Claude
const claudePrompt = `You are an advanced code reviewer and linter specialized in Django/React full-stack applications. Analyze the following code and identify inconsistencies between frontend and backend:

CHANGED FILES (Diffs vs. main branch):
\${DIFFS}

RECENTLY MODIFIED FILES:
\${MODIFIED_FILES}

BACKEND STRUCTURE:
\${BACKEND_STRUCTURE}

FRONTEND STRUCTURE:
\${FRONTEND_STRUCTURE}

API ENDPOINTS:
\${API_ENDPOINTS}

API USAGE:
\${API_USAGE}

SERIALIZER AND PROP TYPE CORRELATION:
\${SERIALIZER_PROP_CORRELATION}

DEPENDENCIES BETWEEN FILES:
\${DEPENDENCIES}

Based on this information, identify:

1. CRITICAL ISSUES:
   - API endpoint mismatches between Django URLs and React API calls
   - Data structure inconsistencies between Django models and React state/props
   - Missing error handling for API calls
   - Security vulnerabilities
   - Serializer field mismatches with React prop types

2. IMPORTANT ISSUES:
   - Django model fields that don't match React component props/state
   - Missing validation in forms
   - Performance bottlenecks in API calls or React rendering
   - Authentication/authorization issues
   - Inconsistent typing between serializers and components

3. STANDARD ISSUES:
   - Code style inconsistencies
   - Potential bugs in either frontend or backend
   - Edge cases not handled
   - Missing documentation

For each issue found, format your response exactly as follows:
FILENAME:LINE_NUMBER
ISSUE: Brief description of the problem
FIX: Specific recommendation on how to fix it
SEVERITY: [Critical/High/Medium/Low]
RELATED_FILES: [List any files affected by or related to this issue]
AUTO_FIX: [If available, provide exact code replacement to fix the issue]
---

When providing AUTO_FIX, make sure it's a precise code snippet that can be automatically applied to fix the issue. For complex fixes that can't be automated, leave the AUTO_FIX field empty.

Sort issues by severity, then by filename and line number. Only report actual issues - do not include compliments or other text.`;

// Get git diffs
function getGitDiffs() {
  try {
    // Check if git is available
    try {
      execSync(`${GIT_PATH} --version`, { stdio: 'ignore' });
    } catch (error) {
      return "Git not available. Skipping diff analysis.";
    }
    
    // Get list of changed files
    const changedFiles = execSync(`${GIT_PATH} diff --name-only origin/main`).toString().trim().split('\n');
    if (!changedFiles[0]) return "No changed files detected.";

    let diffs = "";
    for (const file of changedFiles) {
      if (!file || !fs.existsSync(file)) continue;
      diffs += `--- ${file} ---\n`;
      diffs += execSync(`${GIT_PATH} diff origin/main -- "${file}"`).toString().trim() + "\n\n";
    }
    return diffs || "No meaningful diffs detected.";
  } catch (error) {
    return `Skipping git diffs: ${error.message}`;
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

// Extract Django models structure
function extractDjangoModels() {
  try {
    // Find all Django models.py files
    let modelFiles = [];
    try {
      modelFiles = execSync('find . -type f -name "models.py" | grep -v "migrations"').toString().trim().split('\n');
    } catch (findError) {
      return "Error finding Django model files. Make sure 'find' command is available.";
    }
    
    if (!modelFiles[0]) return "No Django model files found.";
    
    let modelsStructure = "DJANGO MODELS STRUCTURE:\n\n";
    
    for (const modelFile of modelFiles) {
      if (!modelFile || !fs.existsSync(modelFile)) continue;
      
      const appName = path.dirname(modelFile).split(path.sep).pop();
      modelsStructure += `APP: ${appName}\n`;
      
      const fileContent = fs.readFileSync(modelFile, 'utf8');
      
      // Extract model classes
      const modelRegex = /class\s+(\w+)\(.*\):/g;
      let modelMatch;
      
      while ((modelMatch = modelRegex.exec(fileContent)) !== null) {
        const modelName = modelMatch[1];
        modelsStructure += `  MODEL: ${modelName}\n`;
        
        // Find the model definition's end
        const modelStartIdx = modelMatch.index;
        let modelEndIdx = fileContent.length;
        
        // Simple heuristic to find the end of the model class
        // (finds the next class or end of file)
        const nextClassMatch = /class\s+\w+\(.*\):/g;
        nextClassMatch.lastIndex = modelStartIdx + 1;
        const nextMatch = nextClassMatch.exec(fileContent);
        if (nextMatch) {
          modelEndIdx = nextMatch.index;
        }
        
        const modelDef = fileContent.substring(modelStartIdx, modelEndIdx);
        
        // Extract fields
        const fieldRegex = /(\w+)\s*=\s*models\.(\w+)\(([^)]*)\)/g;
        let fieldMatch;
        
        while ((fieldMatch = fieldRegex.exec(modelDef)) !== null) {
          const fieldName = fieldMatch[1];
          const fieldType = fieldMatch[2];
          const fieldArgs = fieldMatch[3].trim();
          
          modelsStructure += `    FIELD: ${fieldName} (${fieldType}${fieldArgs ? ', ' + fieldArgs : ''})\n`;
        }
        
        // Extract foreign keys and relationships
        const relRegex = /(\w+)\s*=\s*models\.(ForeignKey|OneToOneField|ManyToManyField)\('?(\w+)'?/g;
        let relMatch;
        
        while ((relMatch = relRegex.exec(modelDef)) !== null) {
          const fieldName = relMatch[1];
          const relationType = relMatch[2];
          const relatedModel = relMatch[3];
          
          modelsStructure += `    RELATION: ${fieldName} (${relationType} to ${relatedModel})\n`;
        }
      }
      
      modelsStructure += '\n';
    }
    
    return modelsStructure;
  } catch (error) {
    return `Error extracting Django models: ${error.message}`;
  }
}

// Extract React component structure
function extractReactComponents() {
  try {
    // Find all React component files (JSX)
    let jsxFiles = [];
    try {
      jsxFiles = execSync('find ./frontend -type f -name "*.jsx" | grep -v "node_modules"').toString().trim().split('\n');
    } catch (findError) {
      return { 
        componentsStructure: "Error finding React component files. Make sure 'find' command is available or frontend directory exists.",
        allComponents: {}
      };
    }
    
    if (!jsxFiles[0]) return { 
      componentsStructure: "No React component files found.",
      allComponents: {}
    };
    
    let componentsStructure = "REACT COMPONENTS STRUCTURE:\n\n";
    
    // Track all components and their props/state
    const allComponents = {};
    
    for (const jsxFile of jsxFiles) {
      if (!jsxFile || !fs.existsSync(jsxFile)) continue;
      
      const componentName = path.basename(jsxFile, '.jsx');
      const relativePath = path.relative('.', jsxFile);
      componentsStructure += `COMPONENT: ${componentName} (${relativePath})\n`;
      
      const fileContent = fs.readFileSync(jsxFile, 'utf8');
      
      // Initialize component data structure
      const componentData = {
        name: componentName,
        file: jsxFile,
        props: [],
        state: [],
        apiCalls: [],
        formFields: []
      };
      
      // Look for prop destructuring in functional components with more comprehensive regex
      // This handles both the basic case and more complex destructuring patterns
      const propRegex = /(?:function\s+\w+|\bconst\s+\w+\s*=\s*(?:React\.)?(?:memo\()?(?:\(|\s+))\s*\(\s*(?:props|\{([^}]*)\})/g;
      let propMatch;
      const propNames = new Set();
      
      while ((propMatch = propRegex.exec(fileContent)) !== null) {
        if (propMatch[1]) { // We have destructured props
          const props = propMatch[1].split(',')
            .map(p => {
              // Handle default values and renaming
              const propParts = p.trim().split(/\s*=\s*|\s*:\s*/);
              return propParts[0].trim();
            })
            .filter(p => p && !p.includes('...'));
            
          if (props.length > 0) {
            componentsStructure += `  PROPS: ${props.join(', ')}\n`;
            props.forEach(prop => {
              if (!propNames.has(prop)) {
                propNames.add(prop);
                
                // Try to infer prop type from usage
                let propType = 'unknown';
                const defaultValueMatch = new RegExp(`${prop}\\s*=\\s*(?:{([^}]*)}|"([^"]*)")`).exec(fileContent);
                if (defaultValueMatch) {
                  const value = defaultValueMatch[1] || defaultValueMatch[2];
                  if (value === 'true' || value === 'false') propType = 'boolean';
                  else if (!isNaN(value)) propType = 'number';
                  else if (defaultValueMatch[2]) propType = 'string';
                  else if (value === '[]') propType = 'array';
                  else if (value === '{}') propType = 'object';
                }
                
                componentData.props.push({
                  name: prop,
                  type: propType
                });
              }
            });
          }
        } else { // We have 'props' as a single parameter
          // Look for props usage in the component
          const propsUsageRegex = /props\.(\w+)/g;
          let propsMatch;
          while ((propsMatch = propsUsageRegex.exec(fileContent)) !== null) {
            const propName = propsMatch[1];
            if (!propNames.has(propName)) {
              propNames.add(propName);
              componentsStructure += `  PROP: ${propName}\n`;
              componentData.props.push({
                name: propName,
                type: 'unknown'
              });
            }
          }
        }
      }
      
      // Look for PropTypes definitions
      const propTypesRegex = /(?:componentName|[\w.]+)\.propTypes\s*=\s*{([^}]*)}/;
      const propTypesMatch = propTypesRegex.exec(fileContent);
      if (propTypesMatch) {
        const propTypesDef = propTypesMatch[1];
        const propTypeEntries = propTypesDef.split(',');
        
        for (const entry of propTypeEntries) {
          const entryMatch = /(\w+)\s*:\s*PropTypes\.(\w+)/.exec(entry);
          if (entryMatch) {
            const propName = entryMatch[1];
            const propType = entryMatch[2];
            
            // Update the prop type if we found it
            const existingProp = componentData.props.find(p => p.name === propName);
            if (existingProp) {
              existingProp.type = propType;
              componentsStructure += `  PROPTYPE: ${propName} (${propType})\n`;
            } else {
              componentData.props.push({
                name: propName,
                type: propType
              });
              componentsStructure += `  PROPTYPE: ${propName} (${propType})\n`;
            }
          }
        }
      }
      
      // Look for useState hooks to understand component state
      const stateRegex = /const\s+\[(\w+),\s*set(\w+)\]\s*=\s*useState(?:<([^>]*)>)?\(([^)]*)\)/g;
      let stateMatch;
      
      while ((stateMatch = stateRegex.exec(fileContent)) !== null) {
        const stateName = stateMatch[1];
        const typeAnnotation = stateMatch[3] || '';
        const initialValue = stateMatch[4].trim();
        
        // Infer state type
        let stateType = 'unknown';
        if (typeAnnotation) {
          stateType = typeAnnotation;
        } else if (initialValue === '[]') {
          stateType = 'array';
        } else if (initialValue === '{}') {
          stateType = 'object';
        } else if (initialValue === 'true' || initialValue === 'false') {
          stateType = 'boolean';
        } else if (!isNaN(initialValue) && initialValue !== '') {
          stateType = 'number';
        } else if (initialValue.startsWith('"') || initialValue.startsWith("'")) {
          stateType = 'string';
        }
        
        componentsStructure += `  STATE: ${stateName} (${stateType}, ${initialValue || 'no initial value'})\n`;
        componentData.state.push({
          name: stateName,
          type: stateType,
          initialValue: initialValue
        });
      }
      
      // Look for API calls with endpoint patterns
      const apiCallPatterns = [
        { regex: /fetch\(\s*['"](\/api\/[^'"]*)['"]/g, method: 'fetch' },
        { regex: /axios\.\w+\(\s*['"](\/api\/[^'"]*)['"]/g, method: 'axios' },
        { regex: /apiClient\.\w+\(\s*['"](\/api\/[^'"]*)['"]/g, method: 'apiClient' }
      ];
      
      let hasApiCalls = false;
      for (const pattern of apiCallPatterns) {
        let apiMatch;
        while ((apiMatch = pattern.regex.exec(fileContent)) !== null) {
          const endpoint = apiMatch[1];
          hasApiCalls = true;
          componentData.apiCalls.push({
            method: pattern.method,
            endpoint: endpoint
          });
          componentsStructure += `  API CALL: ${pattern.method} to ${endpoint}\n`;
        }
      }
      
      if (hasApiCalls) {
        componentsStructure += `  API CALLS: This component makes API requests\n`;
      }
      
      // Look for form fields
      const formFieldRegex = /<(?:Input|TextField|Select|Checkbox)\s+(?:[^>]*name=["'](\w+)["'][^>]*)/g;
      let formFieldMatch;
      
      while ((formFieldMatch = formFieldRegex.exec(fileContent)) !== null) {
        const fieldName = formFieldMatch[1];
        if (fieldName) {
          componentsStructure += `  FORM FIELD: ${fieldName}\n`;
          componentData.formFields.push(fieldName);
        }
      }
      
      // Store component data for correlation
      allComponents[componentName] = componentData;
      
      componentsStructure += '\n';
    }
    
    return { componentsStructure, allComponents };
  } catch (error) {
    return { 
      componentsStructure: `Error extracting React components: ${error.message}`,
      allComponents: {}
    };
  }
}

// Extract DRF serializers
function extractDjangoSerializers() {
  try {
    // Find all Django serializers.py files
    let serializerFiles = [];
    try {
      serializerFiles = execSync('find . -type f -name "serializers.py" | grep -v "migrations"').toString().trim().split('\n');
    } catch (findError) {
      return { 
        serializersStructure: "Error finding Django serializer files. Make sure 'find' command is available.",
        allSerializers: {}
      };
    }
    
    if (!serializerFiles[0]) return { 
      serializersStructure: "No Django REST Framework serializer files found.",
      allSerializers: {}
    };
    
    let serializersStructure = "DJANGO REST FRAMEWORK SERIALIZERS:\n\n";
    
    // Track all serializers and their fields
    const allSerializers = {};
    
    for (const serializerFile of serializerFiles) {
      if (!serializerFile || !fs.existsSync(serializerFile)) continue;
      
      const appName = path.dirname(serializerFile).split(path.sep).pop();
      serializersStructure += `APP: ${appName}\n`;
      
      const fileContent = fs.readFileSync(serializerFile, 'utf8');
      
      // Extract serializer classes
      const serializerRegex = /class\s+(\w+)(?:Serializer)?\(.*Serializer.*\):/g;
      let serializerMatch;
      
      while ((serializerMatch = serializerRegex.exec(fileContent)) !== null) {
        const serializerName = serializerMatch[1];
        serializersStructure += `  SERIALIZER: ${serializerName}\n`;
        
        // Find the serializer definition's end
        const serializerStartIdx = serializerMatch.index;
        let serializerEndIdx = fileContent.length;
        
        // Simple heuristic to find the end of the serializer class
        const nextClassMatch = /class\s+\w+\(.*\):/g;
        nextClassMatch.lastIndex = serializerStartIdx + 1;
        const nextMatch = nextClassMatch.exec(fileContent);
        if (nextMatch) {
          serializerEndIdx = nextMatch.index;
        }
        
        const serializerDef = fileContent.substring(serializerStartIdx, serializerEndIdx);
        
        // Initialize serializer data structure
        const serializerData = {
          name: serializerName,
          app: appName,
          fields: [],
          file: serializerFile
        };
        
        // Extract explicitly defined fields
        const fieldRegex = /(\w+)\s*=\s*serializers\.(\w+)\(([^)]*)\)/g;
        let fieldMatch;
        
        while ((fieldMatch = fieldRegex.exec(serializerDef)) !== null) {
          const fieldName = fieldMatch[1];
          const fieldType = fieldMatch[2];
          const fieldArgs = fieldMatch[3].trim();
          
          serializersStructure += `    FIELD: ${fieldName} (${fieldType}${fieldArgs ? ', ' + fieldArgs : ''})\n`;
          serializerData.fields.push({
            name: fieldName,
            type: fieldType,
            args: fieldArgs
          });
        }
        
        // Extract Meta class model fields
        const metaClassRegex = /class\s+Meta:[\s\S]*?fields\s*=\s*(\[.*?\]|\(.*?\)|['"]__all__['"])/;
        const metaMatch = metaClassRegex.exec(serializerDef);
        if (metaMatch) {
          const fieldsStr = metaMatch[1].trim();
          serializersStructure += `    META: fields=${fieldsStr}\n`;
          
          // Add meta info to serializer data
          serializerData.meta = {
            fields: fieldsStr
          };
          
          // If using __all__, extract model name to potentially look up fields
          if (fieldsStr.includes('__all__')) {
            const modelRegex = /model\s*=\s*(\w+)/;
            const modelMatch = modelRegex.exec(serializerDef);
            if (modelMatch) {
              serializerData.meta.model = modelMatch[1];
            }
          }
        }
        
        // Store serializer data for correlation
        allSerializers[`${appName}.${serializerName}`] = serializerData;
      }
      
      serializersStructure += '\n';
    }
    
    return { serializersStructure, allSerializers };
  } catch (error) {
    return { 
      serializersStructure: `Error extracting Django serializers: ${error.message}`,
      allSerializers: {}
    };
  }
}

// Extract Django API endpoints
function extractDjangoApiEndpoints() {
  try {
    // Find all Django urls.py files
    let urlsFiles = [];
    try {
      urlsFiles = execSync('find . -type f -name "urls.py" | grep -v "migrations"').toString().trim().split('\n');
    } catch (findError) {
      return "Error finding Django URL files. Make sure 'find' command is available.";
    }
    
    if (!urlsFiles[0]) return "No Django URL configuration files found.";
    
    let endpointsStructure = "DJANGO API ENDPOINTS:\n\n";
    
    for (const urlsFile of urlsFiles) {
      if (!urlsFile || !fs.existsSync(urlsFile)) continue;
      
      const appName = path.dirname(urlsFile).split(path.sep).pop();
      endpointsStructure += `APP: ${appName}\n`;
      
      const fileContent = fs.readFileSync(urlsFile, 'utf8');
      
      // Extract path patterns from path()
      const pathRegex = /path\(['"]([^'"]*)['"]\s*,\s*(\w+(?:\.\w+)*)\s*(?:,\s*name=['"]([^'"]*)['"]\s*)?\)/g;
      let pathMatch;
      
      while ((pathMatch = pathRegex.exec(fileContent)) !== null) {
        const urlPattern = pathMatch[1];
        const viewFunction = pathMatch[2];
        const urlName = pathMatch[3] || '(unnamed)';
        
        endpointsStructure += `  ENDPOINT: ${urlPattern} → ${viewFunction} (${urlName})\n`;
      }
      
      // Extract router registrations (DRF)
      const routerRegex = /router\.register\(['"]([^'"]*)['"]\s*,\s*(\w+(?:\.\w+)*)\s*(?:,\s*['"]([^'"]*)['"]\s*)?\)/g;
      let routerMatch;
      
      while ((routerMatch = routerRegex.exec(fileContent)) !== null) {
        const urlPrefix = routerMatch[1];
        const viewSet = routerMatch[2];
        const basenameOrNone = routerMatch[3] || '(default basename)';
        
        endpointsStructure += `  API ROUTER: ${urlPrefix} → ${viewSet} (${basenameOrNone})\n`;
      }
      
      endpointsStructure += '\n';
    }
    
    return endpointsStructure;
  } catch (error) {
    return `Error extracting Django API endpoints: ${error.message}`;
  }
}

// Correlate Django serializers with React components
function correlateSerializersWithComponents(allSerializers, allComponents) {
  try {
    let correlationStructure = "SERIALIZER AND COMPONENT CORRELATION:\n\n";
    const correlations = [];
    
    // For each component, try to find matching serializers
    for (const [componentName, component] of Object.entries(allComponents)) {
      // Skip components without props or API calls
      if (component.props.length === 0 || component.apiCalls.length === 0) {
        continue;
      }
      
      correlationStructure += `COMPONENT: ${componentName}\n`;
      
      // Look at component API calls and form fields to guess potential serializer matches
      const potentialMatches = new Set();
      
      // Check component props and state against serializer fields
      const componentFields = [
        ...component.props.map(p => p.name.toLowerCase()),
        ...component.state.map(s => s.name.toLowerCase()),
        ...component.formFields.map(f => f.toLowerCase())
      ];
      
      // For each serializer, check if fields match
      for (const [serializerKey, serializer] of Object.entries(allSerializers)) {
        const serializerFields = serializer.fields.map(f => f.name.toLowerCase());
        
        // Count matching fields
        const matchingFields = componentFields.filter(field => 
          serializerFields.includes(field)
        );
        
        // If we have a significant number of matching fields, consider it a potential match
        // (At least 3 matching fields or 50% of the smaller set)
        const matchThreshold = Math.min(3, Math.floor(Math.min(componentFields.length, serializerFields.length) * 0.5));
        
        if (matchingFields.length >= matchThreshold) {
          potentialMatches.add(serializerKey);
          
          correlationStructure += `  POTENTIAL SERIALIZER MATCH: ${serializerKey}\n`;
          correlationStructure += `    MATCHING FIELDS: ${matchingFields.join(', ')}\n`;
          
          // Add to correlations list
          correlations.push({
            component: componentName,
            componentFile: component.file,
            serializer: serializerKey,
            serializerFile: serializer.file,
            matchingFields,
            mismatchedFields: componentFields.filter(f => !serializerFields.includes(f))
          });
        }
      }
      
      if (potentialMatches.size === 0) {
        correlationStructure += `  NO POTENTIAL SERIALIZER MATCHES FOUND\n`;
      }
      
      correlationStructure += '\n';
    }
    
    return { correlationStructure, correlations };
  } catch (error) {
    return {
      correlationStructure: `Error correlating serializers with components: ${error.message}`,
      correlations: []
    };
  }
}

// Extract React API usage
function extractReactApiUsage() {
  try {
    // Find all JS/JSX files that might contain API calls
    let jsFiles = [];
    try {
      jsFiles = execSync('find ./frontend -type f \\( -name "*.js" -o -name "*.jsx" \\) | grep -v "node_modules"').toString().trim().split('\n');
    } catch (findError) {
      return "Error finding React JS/JSX files. Make sure 'find' command is available or frontend directory exists.";
    }
    
    if (!jsFiles[0]) return "No React JavaScript files found.";
    
    let apiUsageStructure = "REACT API USAGE:\n\n";
    
    // Track API endpoints found
    const apiEndpoints = new Set();
    
    for (const jsFile of jsFiles) {
      if (!jsFile || !fs.existsSync(jsFile)) continue;
      
      const fileContent = fs.readFileSync(jsFile, 'utf8');
      const fileName = path.basename(jsFile);
      
      // Look for fetch calls
      const fetchRegex = /fetch\(\s*['"](\/api\/[^'"]*)['"]/g;
      let fetchMatch;
      const fetchEndpoints = [];
      
      while ((fetchMatch = fetchRegex.exec(fileContent)) !== null) {
        const endpoint = fetchMatch[1];
        fetchEndpoints.push(endpoint);
        apiEndpoints.add(endpoint);
      }
      
      // Look for axios calls
      const axiosRegex = /axios\.\w+\(\s*['"](\/api\/[^'"]*)['"]/g;
      let axiosMatch;
      const axiosEndpoints = [];
      
      while ((axiosMatch = axiosRegex.exec(fileContent)) !== null) {
        const endpoint = axiosMatch[1];
        axiosEndpoints.push(endpoint);
        apiEndpoints.add(endpoint);
      }
      
      // Look for custom API client calls
      const apiClientRegex = /apiClient\.\w+\(\s*['"](\/api\/[^'"]*)['"]/g;
      let apiClientMatch;
      const apiClientEndpoints = [];
      
      while ((apiClientMatch = apiClientRegex.exec(fileContent)) !== null) {
        const endpoint = apiClientMatch[1];
        apiClientEndpoints.push(endpoint);
        apiEndpoints.add(endpoint);
      }
      
      // Look for string constants that might be API URLs
      const urlConstRegex = /const\s+\w+_URL\s*=\s*['"](\/api\/[^'"]*)['"]/g;
      let urlConstMatch;
      const urlConstants = [];
      
      while ((urlConstMatch = urlConstRegex.exec(fileContent)) !== null) {
        const endpoint = urlConstMatch[1];
        urlConstants.push(endpoint);
        apiEndpoints.add(endpoint);
      }
      
      // Only add to output if we found endpoints
      if (fetchEndpoints.length || axiosEndpoints.length || apiClientEndpoints.length || urlConstants.length) {
        apiUsageStructure += `FILE: ${fileName}\n`;
        
        if (fetchEndpoints.length) {
          apiUsageStructure += `  FETCH ENDPOINTS: ${fetchEndpoints.join(', ')}\n`;
        }
        
        if (axiosEndpoints.length) {
          apiUsageStructure += `  AXIOS ENDPOINTS: ${axiosEndpoints.join(', ')}\n`;
        }
        
        if (apiClientEndpoints.length) {
          apiUsageStructure += `  API CLIENT ENDPOINTS: ${apiClientEndpoints.join(', ')}\n`;
        }
        
        if (urlConstants.length) {
          apiUsageStructure += `  URL CONSTANTS: ${urlConstants.join(', ')}\n`;
        }
        
        apiUsageStructure += '\n';
      }
    }
    
    apiUsageStructure += "SUMMARY OF ALL FRONTEND API ENDPOINTS:\n";
    Array.from(apiEndpoints).sort().forEach(endpoint => {
      apiUsageStructure += `  ${endpoint}\n`;
    });
    
    return apiUsageStructure;
  } catch (error) {
    return `Error extracting React API usage: ${error.message}`;
  }
}

// Build dependency graph (enhanced for Python & JavaScript)
function analyzeDependencies(modifiedFiles = []) {
  try {
    // Include both JS/TS and Python files
    const allJsFiles = execSync('find . -type f \\( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \\) | grep -v "node_modules"').toString().trim().split('\n');
    const allPyFiles = execSync('find . -type f -name "*.py" | grep -v "__pycache__" | grep -v "migrations"').toString().trim().split('\n');
    
    const allFiles = [...allJsFiles, ...allPyFiles].filter(Boolean);
    
    const dependencies = {};
    const reverseDependencies = {};
    
    // Build forward and reverse dependency mappings
    for (const file of allFiles) {
      if (!file) continue;
      
      const content = fs.readFileSync(file, 'utf8');
      const ext = path.extname(file);
      let deps = [];
      
      if (ext === '.js' || ext === '.jsx' || ext === '.ts' || ext === '.tsx') {
        // JS/TS import patterns
        const importRegex = /(?:import|require)\s*\(?(?:['"]([^'"]+)['"]\)?|{[^}]*}\s+from\s+['"]([^'"]+)['"]\)?)/g;
        let match;
        
        while ((match = importRegex.exec(content)) !== null) {
          const importPath = match[1] || match[2];
          if (!importPath || !importPath.startsWith('.')) continue; // Skip external packages
          
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
      } else if (ext === '.py') {
        // Python import patterns
        
        // Regular import statements (import x.y.z)
        const importRegex = /import\s+([\w.]+)/g;
        let match;
        
        while ((match = importRegex.exec(content)) !== null) {
          const importPath = match[1];
          // Convert Python import to file path
          const possiblePath = importPath.replace(/\./g, path.sep) + '.py';
          
          // Check if it's a local module
          try {
            const dir = path.dirname(file);
            let moduleRoot = dir;
            
            // Try to find the most appropriate module root
            while (moduleRoot && moduleRoot !== '.') {
              const testPath = path.join(moduleRoot, possiblePath);
              if (fs.existsSync(testPath)) {
                deps.push(testPath);
                break;
              }
              moduleRoot = path.dirname(moduleRoot);
            }
          } catch (e) {
            // Skip if we can't resolve
          }
        }
        
        // From import statements (from x.y import z)
        const fromImportRegex = /from\s+([\w.]+)\s+import\s+/g;
        let fromMatch;
        
        while ((fromMatch = fromImportRegex.exec(content)) !== null) {
          const importPath = fromMatch[1];
          if (importPath === '') continue; // Skip relative imports for now
          
          // Convert Python import to file path
          const possiblePath = importPath.replace(/\./g, path.sep) + '.py';
          
          // Check if it's a local module
          try {
            const dir = path.dirname(file);
            let moduleRoot = dir;
            
            // Try to find the most appropriate module root
            while (moduleRoot && moduleRoot !== '.') {
              const testPath = path.join(moduleRoot, possiblePath);
              if (fs.existsSync(testPath)) {
                deps.push(testPath);
                break;
              }
              moduleRoot = path.dirname(moduleRoot);
            }
          } catch (e) {
            // Skip if we can't resolve
          }
        }
        
        // Relative imports (from . import x, from .. import y)
        const relativeImportRegex = /from\s+(\.+)(?:[\w.]+)?\s+import\s+/g;
        let relMatch;
        
        while ((relMatch = relativeImportRegex.exec(content)) !== null) {
          const dots = relMatch[1];
          const dir = path.dirname(file);
          
          // Calculate parent directory based on number of dots
          let parentDir = dir;
          for (let i = 1; i < dots.length; i++) {
            parentDir = path.dirname(parentDir);
          }
          
          // We don't know exactly which module is imported, but we can mark the directory as a dependency
          deps.push(parentDir);
        }
      }
      
      // Add unique dependencies
      deps = [...new Set(deps)];
      
      if (deps.length > 0) {
        const relPath = file.startsWith('./') ? file.substring(2) : file;
        dependencies[relPath] = deps;
        
        // Build reverse dependency map
        for (const dep of deps) {
          const relDep = dep.startsWith('./') ? dep.substring(2) : dep;
          if (!reverseDependencies[relDep]) {
            reverseDependencies[relDep] = [];
          }
          reverseDependencies[relDep].push(relPath);
        }
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
    result += "JAVASCRIPT/TYPESCRIPT DEPENDENCIES:\n";
    const jsDeps = Object.entries(dependencies).filter(([file]) => 
      file.endsWith('.js') || file.endsWith('.jsx') || file.endsWith('.ts') || file.endsWith('.tsx')
    );
    
    for (const [file, deps] of jsDeps) {
      const isAffected = affectedFiles.includes(file);
      result += `${isAffected ? '[AFFECTED] ' : ''}${file} depends on:\n`;
      deps.forEach(dep => {
        const isDepAffected = affectedFiles.includes(dep);
        result += `  - ${isDepAffected ? '[AFFECTED] ' : ''}${dep}\n`;
      });
      result += '\n';
    }
    
    result += "PYTHON DEPENDENCIES:\n";
    const pyDeps = Object.entries(dependencies).filter(([file]) => file.endsWith('.py'));
    
    for (const [file, deps] of pyDeps) {
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
  ig.add(['node_modules', '.git', 'dist', 'build', '.claude-temp-prompt.txt', '__pycache__', '*.pyc', '*.pyo']);
  return ig;
}

// Run Claude analysis
async function runAnalysis(modifiedFiles = []) {
  console.log("Analyzing code with Claude...");
  console.log("Extracting code structure and dependencies. This may take a moment...");
  
  // Get all required information
  const diffs = getGitDiffs();
  const { analysis: dependencies, affectedFiles } = analyzeDependencies(modifiedFiles);
  const modifiedFilesContent = getModifiedFilesContent(affectedFiles);
  
  console.log("Extracting Django models...");
  const backendStructure = extractDjangoModels();
  
  console.log("Extracting DRF serializers...");
  const { serializersStructure, allSerializers } = extractDjangoSerializers();
  
  console.log("Extracting React components...");
  const { componentsStructure, allComponents } = extractReactComponents();
  
  console.log("Extracting Django API endpoints...");
  const apiEndpoints = extractDjangoApiEndpoints();
  
  console.log("Extracting React API usage...");
  const apiUsage = extractReactApiUsage();
  
  console.log("Correlating serializers with components...");
  const { correlationStructure, correlations } = correlateSerializersWithComponents(allSerializers, allComponents);
  
  // Generate auto-fix suggestions based on correlations
  let autoFixStructure = "AUTO-FIX SUGGESTIONS:\n\n";
  
  if (correlations.length > 0) {
    for (const correlation of correlations) {
      if (correlation.mismatchedFields.length > 0) {
        autoFixStructure += `COMPONENT: ${correlation.component} -> SERIALIZER: ${correlation.serializer}\n`;
        autoFixStructure += `  MISMATCHED FIELDS: ${correlation.mismatchedFields.join(', ')}\n`;
        
        // Suggest prop type fixes
        autoFixStructure += `  SUGGESTED FIXES:\n`;
        for (const field of correlation.mismatchedFields) {
          const componentFilePath = correlation.componentFile;
          autoFixStructure += `    - Add "${field}" to ${correlation.component}\n`;
        }
        autoFixStructure += '\n';
      }
    }
  } else {
    autoFixStructure += "No serializer-component correlations found to suggest fixes for.\n";
  }
  
  // Build final prompt
  const finalPrompt = claudePrompt
    .replace('${DIFFS}', diffs)
    .replace('${MODIFIED_FILES}', modifiedFilesContent)
    .replace('${BACKEND_STRUCTURE}', backendStructure + '\n' + serializersStructure)
    .replace('${FRONTEND_STRUCTURE}', componentsStructure)
    .replace('${API_ENDPOINTS}', apiEndpoints)
    .replace('${API_USAGE}', apiUsage)
    .replace('${SERIALIZER_PROP_CORRELATION}', correlationStructure + '\n' + autoFixStructure)
    .replace('${DEPENDENCIES}', dependencies);
  
  // Write prompt to a temp file to avoid command line length limitations
  fs.writeFileSync('.claude-temp-prompt.txt', finalPrompt);
  
  // Run Claude CLI with the prompt
  try {
    console.log(`Running analysis on ${modifiedFiles.length} modified files and ${affectedFiles.length - modifiedFiles.length} related files...`);
    console.log("Sending code to Claude for analysis...");
    
    // Check if Claude CLI is available
    try {
      execSync('claude --version', { stdio: 'ignore' });
      const result = execSync('claude -p "$(cat .claude-temp-prompt.txt)"').toString();
      
      // Display results with timestamp
      const timestamp = new Date().toLocaleTimeString();
      console.log(`\n=== CLAUDE ANALYSIS RESULTS (${timestamp}) ===\n`);
      console.log(result);
      console.log('\n=== END OF ANALYSIS ===\n');
    } catch (cliError) {
      console.log("Claude CLI not found or not properly configured.");
      console.log("To install Claude CLI, visit: https://github.com/anthropics/claude-cli");
      console.log("\nPrompt has been saved to .claude-temp-prompt.txt for manual analysis.");
      console.log("You can view this file and send its contents to Claude API directly.");
    }
  } catch (error) {
    console.error("Error during analysis:", error.message);
  } finally {
    // We'll keep the temp file for manual inspection if claude CLI isn't available
    if (fs.existsSync('.claude-temp-prompt.txt')) {
      console.log("Prompt file saved at .claude-temp-prompt.txt");
    }
  }
}

// Main function for manual execution
async function main() {
  await runAnalysis([]);
}

// Watcher mode
function watchMode() {
  const ig = getIgnorer();
  console.log("Starting Claude code watcher for Django/React projects...");
  console.log("Monitoring for file changes (press Ctrl+C to exit)...");
  
  // Use chokidar to watch file changes
  const watcher = chokidar.watch('.', {
    ignored: path => {
      const relativePath = path.startsWith('./') ? path.substring(2) : path;
      return ig.ignores(relativePath) || 
             /^\.(git|vscode|idea)/.test(relativePath) ||
             /\.pyc$/.test(relativePath);
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
  
  console.log("Watching for file changes in both Django backend and React frontend...");
}

// Check if we're in watch mode
if (process.argv.includes('--watch') || process.argv.includes('-w')) {
  watchMode();
} else {
  main().catch(console.error);
}
