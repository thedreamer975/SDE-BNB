import { execSync } from 'child_process';
import { existsSync, mkdirSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '../..');
const openapiPath = path.resolve(rootDir, 'docs/openapi.json');
const libDir = path.resolve(__dirname, '../lib');
const outputPath = path.resolve(libDir, 'types.gen.ts');

if (!existsSync(libDir)) {
  mkdirSync(libDir, { recursive: true });
}

// Ensure openapi.json exists by calling export_openapi.py if missing
if (!existsSync(openapiPath)) {
  console.log('OpenAPI schema not found, exporting from backend...');
  const pythonCmd = process.platform === 'win32' 
    ? path.resolve(rootDir, 'backend/.venv/Scripts/python.exe')
    : path.resolve(rootDir, 'backend/.venv/bin/python');
  
  const pyToUse = existsSync(pythonCmd) ? pythonCmd : 'python';
  execSync(`"${pyToUse}" "${path.resolve(rootDir, 'backend/export_openapi.py')}"`, { stdio: 'inherit', cwd: rootDir });
}

console.log(`Generating types from ${openapiPath} to ${outputPath}...`);
execSync(`npx openapi-typescript "${openapiPath}" -o "${outputPath}"`, { stdio: 'inherit' });
console.log('Types generated successfully.');
