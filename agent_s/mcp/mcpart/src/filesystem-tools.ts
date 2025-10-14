import * as fs from 'fs/promises';
import * as path from 'path';
import { promisify } from 'util';
import { exec as execCallback } from 'child_process';

const exec = promisify(execCallback);

// Allowed base directories for filesystem operations
const ALLOWED_DIRECTORIES = [
  '/home/stacy/AlphaOmega/artifacts',
  '/home/stacy/AlphaOmega/logs',
  '/home/stacy/AlphaOmega'
];

// Helper to validate paths are within allowed directories
function isPathAllowed(targetPath: string): boolean {
  const normalizedPath = path.normalize(path.resolve(targetPath));
  return ALLOWED_DIRECTORIES.some(allowed => 
    normalizedPath.startsWith(path.normalize(allowed))
  );
}

// Helper to get file info
async function getFileInfo(filePath: string) {
  const stats = await fs.stat(filePath);
  return {
    path: filePath,
    size: stats.size,
    created: stats.birthtime.toISOString(),
    modified: stats.mtime.toISOString(),
    accessed: stats.atime.toISOString(),
    isDirectory: stats.isDirectory(),
    isFile: stats.isFile(),
    permissions: stats.mode.toString(8).slice(-3)
  };
}

export const filesystemTools = [
  {
    name: 'list_allowed_directories',
    description: 'List all directories that the MCP server has access to. Use this to understand where you can read/write files.',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
  {
    name: 'read_file',
    description: 'Read the complete contents of a file. Works with text files, JSON, markdown, code, etc.',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Absolute path to the file to read' },
      },
      required: ['path'],
    },
  },
  {
    name: 'read_multiple_files',
    description: 'Read multiple files at once. Returns contents of all specified files.',
    inputSchema: {
      type: 'object',
      properties: {
        paths: { 
          type: 'array', 
          items: { type: 'string' },
          description: 'Array of absolute file paths to read' 
        },
      },
      required: ['paths'],
    },
  },
  {
    name: 'write_file',
    description: 'Write content to a file. Creates the file if it doesn\'t exist, overwrites if it does.',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Absolute path where to write the file' },
        content: { type: 'string', description: 'Content to write to the file' },
      },
      required: ['path', 'content'],
    },
  },
  {
    name: 'edit_file',
    description: 'Edit an existing file by replacing specific text. Useful for making targeted changes without rewriting entire file.',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Absolute path to the file to edit' },
        oldText: { type: 'string', description: 'Text to find and replace' },
        newText: { type: 'string', description: 'New text to replace with' },
      },
      required: ['path', 'oldText', 'newText'],
    },
  },
  {
    name: 'create_directory',
    description: 'Create a new directory. Will create parent directories if they don\'t exist.',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Absolute path of directory to create' },
      },
      required: ['path'],
    },
  },
  {
    name: 'list_directory',
    description: 'List all files and directories in a given path. Shows names and types (file/directory).',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Absolute path to the directory to list' },
      },
      required: ['path'],
    },
  },
  {
    name: 'directory_tree',
    description: 'Get a recursive tree view of a directory structure. Shows nested files and folders.',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Absolute path to the directory' },
        maxDepth: { type: 'number', description: 'Maximum depth to recurse (default: 3)' },
      },
      required: ['path'],
    },
  },
  {
    name: 'move_file',
    description: 'Move or rename a file or directory.',
    inputSchema: {
      type: 'object',
      properties: {
        source: { type: 'string', description: 'Current path of file/directory' },
        destination: { type: 'string', description: 'New path for file/directory' },
      },
      required: ['source', 'destination'],
    },
  },
  {
    name: 'search_files',
    description: 'Search for files by name pattern or content. Supports glob patterns and regex.',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Directory to search in' },
        pattern: { type: 'string', description: 'File name pattern or search term' },
        searchContent: { type: 'boolean', description: 'If true, search file contents instead of names' },
      },
      required: ['path', 'pattern'],
    },
  },
  {
    name: 'get_file_info',
    description: 'Get detailed metadata about a file or directory (size, dates, permissions).',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Absolute path to file or directory' },
      },
      required: ['path'],
    },
  },
  {
    name: 'read_text_file',
    description: 'Read a text file with specific encoding. Useful for non-UTF8 files.',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Absolute path to the file' },
        encoding: { type: 'string', description: 'Text encoding (utf8, ascii, latin1, etc.)', default: 'utf8' },
      },
      required: ['path'],
    },
  },
  {
    name: 'read_media_file',
    description: 'Read a media file (image, audio, video) as base64. Useful for processing binary files.',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Absolute path to the media file' },
      },
      required: ['path'],
    },
  },
  {
    name: 'list_directory_with_sizes',
    description: 'List directory contents with file sizes and modification dates. More detailed than list_directory.',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Absolute path to the directory' },
      },
      required: ['path'],
    },
  },
];

export async function handleFilesystemTool(name: string, args: any): Promise<string> {
  try {
    switch (name) {
      case 'list_allowed_directories':
        return `Allowed directories:\n${ALLOWED_DIRECTORIES.join('\n')}`;

      case 'read_file':
      case 'read_text_file': {
        const { path: filePath, encoding = 'utf8' } = args;
        if (!isPathAllowed(filePath)) {
          throw new Error(`Access denied: ${filePath} is outside allowed directories`);
        }
        const content = await fs.readFile(filePath, encoding as BufferEncoding);
        return content;
      }

      case 'read_multiple_files': {
        const { paths } = args;
        const results = await Promise.all(
          paths.map(async (filePath: string) => {
            if (!isPathAllowed(filePath)) {
              return { path: filePath, error: 'Access denied: outside allowed directories' };
            }
            try {
              const content = await fs.readFile(filePath, 'utf8');
              return { path: filePath, content };
            } catch (error: any) {
              return { path: filePath, error: error.message };
            }
          })
        );
        return JSON.stringify(results, null, 2);
      }

      case 'read_media_file': {
        const { path: filePath } = args;
        if (!isPathAllowed(filePath)) {
          throw new Error(`Access denied: ${filePath} is outside allowed directories`);
        }
        const buffer = await fs.readFile(filePath);
        return buffer.toString('base64');
      }

      case 'write_file': {
        const { path: filePath, content } = args;
        if (!isPathAllowed(filePath)) {
          throw new Error(`Access denied: ${filePath} is outside allowed directories`);
        }
        // Ensure directory exists
        await fs.mkdir(path.dirname(filePath), { recursive: true });
        await fs.writeFile(filePath, content, 'utf8');
        return `Successfully wrote to ${filePath}`;
      }

      case 'edit_file': {
        const { path: filePath, oldText, newText } = args;
        if (!isPathAllowed(filePath)) {
          throw new Error(`Access denied: ${filePath} is outside allowed directories`);
        }
        const content = await fs.readFile(filePath, 'utf8');
        if (!content.includes(oldText)) {
          throw new Error(`Text not found in file: "${oldText.substring(0, 50)}..."`);
        }
        const newContent = content.replace(oldText, newText);
        await fs.writeFile(filePath, newContent, 'utf8');
        return `Successfully edited ${filePath}`;
      }

      case 'create_directory': {
        const { path: dirPath } = args;
        if (!isPathAllowed(dirPath)) {
          throw new Error(`Access denied: ${dirPath} is outside allowed directories`);
        }
        await fs.mkdir(dirPath, { recursive: true });
        return `Successfully created directory ${dirPath}`;
      }

      case 'list_directory': {
        const { path: dirPath } = args;
        if (!isPathAllowed(dirPath)) {
          throw new Error(`Access denied: ${dirPath} is outside allowed directories`);
        }
        const entries = await fs.readdir(dirPath, { withFileTypes: true });
        const formatted = entries.map(entry => 
          `${entry.isDirectory() ? '📁' : '📄'} ${entry.name}`
        ).join('\n');
        return formatted || 'Directory is empty';
      }

      case 'list_directory_with_sizes': {
        const { path: dirPath } = args;
        if (!isPathAllowed(dirPath)) {
          throw new Error(`Access denied: ${dirPath} is outside allowed directories`);
        }
        const entries = await fs.readdir(dirPath, { withFileTypes: true });
        const details = await Promise.all(
          entries.map(async entry => {
            const fullPath = path.join(dirPath, entry.name);
            const stats = await fs.stat(fullPath);
            const size = entry.isFile() ? `${(stats.size / 1024).toFixed(2)} KB` : '-';
            const modified = stats.mtime.toISOString().split('T')[0];
            return `${entry.isDirectory() ? '📁' : '📄'} ${entry.name.padEnd(30)} ${size.padStart(12)} ${modified}`;
          })
        );
        return details.join('\n') || 'Directory is empty';
      }

      case 'directory_tree': {
        const { path: dirPath, maxDepth = 3 } = args;
        if (!isPathAllowed(dirPath)) {
          throw new Error(`Access denied: ${dirPath} is outside allowed directories`);
        }

        async function buildTree(currentPath: string, depth: number, prefix: string = ''): Promise<string> {
          if (depth > maxDepth) return '';
          
          const entries = await fs.readdir(currentPath, { withFileTypes: true });
          let result = '';
          
          for (let i = 0; i < entries.length; i++) {
            const entry = entries[i];
            const isLast = i === entries.length - 1;
            const connector = isLast ? '└── ' : '├── ';
            const icon = entry.isDirectory() ? '📁' : '📄';
            
            result += `${prefix}${connector}${icon} ${entry.name}\n`;
            
            if (entry.isDirectory() && depth < maxDepth) {
              const newPrefix = prefix + (isLast ? '    ' : '│   ');
              const fullPath = path.join(currentPath, entry.name);
              result += await buildTree(fullPath, depth + 1, newPrefix);
            }
          }
          return result;
        }

        const tree = await buildTree(dirPath, 0);
        return `📁 ${path.basename(dirPath)}\n${tree}`;
      }

      case 'move_file': {
        const { source, destination } = args;
        if (!isPathAllowed(source) || !isPathAllowed(destination)) {
          throw new Error(`Access denied: paths must be within allowed directories`);
        }
        await fs.rename(source, destination);
        return `Successfully moved ${source} to ${destination}`;
      }

      case 'search_files': {
        const { path: searchPath, pattern, searchContent = false } = args;
        if (!isPathAllowed(searchPath)) {
          throw new Error(`Access denied: ${searchPath} is outside allowed directories`);
        }

        if (searchContent) {
          // Search file contents using grep
          const { stdout } = await exec(`grep -r -l "${pattern}" "${searchPath}" 2>/dev/null || true`);
          const files = stdout.trim().split('\n').filter(f => f);
          return files.length > 0 
            ? `Found in ${files.length} files:\n${files.join('\n')}`
            : 'No matches found';
        } else {
          // Search file names using find
          const { stdout } = await exec(`find "${searchPath}" -name "*${pattern}*" 2>/dev/null || true`);
          const files = stdout.trim().split('\n').filter(f => f);
          return files.length > 0
            ? `Found ${files.length} files:\n${files.join('\n')}`
            : 'No matches found';
        }
      }

      case 'get_file_info': {
        const { path: filePath } = args;
        if (!isPathAllowed(filePath)) {
          throw new Error(`Access denied: ${filePath} is outside allowed directories`);
        }
        const info = await getFileInfo(filePath);
        return JSON.stringify(info, null, 2);
      }

      default:
        throw new Error(`Unknown filesystem tool: ${name}`);
    }
  } catch (error: any) {
    throw new Error(`Filesystem operation failed: ${error.message}`);
  }
}
