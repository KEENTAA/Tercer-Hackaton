import { ChangeDetectionStrategy, Component, input, computed } from '@angular/core';

const LANG_KEYWORDS: Record<string, string[]> = {
  python: ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'with', 'as', 'in', 'not', 'and', 'or', 'True', 'False', 'None', 'self', 'lambda', 'yield', 'raise', 'pass', 'break', 'continue', 'async', 'await'],
  java: ['public', 'private', 'protected', 'static', 'void', 'class', 'interface', 'extends', 'implements', 'import', 'package', 'return', 'if', 'else', 'for', 'while', 'try', 'catch', 'finally', 'throw', 'new', 'this', 'super', 'abstract', 'final', 'synchronized', 'volatile', 'transient', 'native', 'assert', 'enum', 'switch', 'case', 'break', 'continue', 'default', 'instanceof'],
  javascript: ['const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while', 'switch', 'case', 'break', 'continue', 'try', 'catch', 'finally', 'throw', 'class', 'extends', 'import', 'export', 'from', 'default', 'async', 'await', 'new', 'this', 'typeof', 'instanceof', 'void', 'delete', 'in', 'of', 'yield', 'null', 'undefined', 'true', 'false'],
  typescript: ['const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while', 'switch', 'case', 'break', 'continue', 'try', 'catch', 'finally', 'throw', 'class', 'extends', 'implements', 'interface', 'type', 'import', 'export', 'from', 'default', 'async', 'await', 'new', 'this', 'typeof', 'instanceof', 'void', 'delete', 'in', 'of', 'yield', 'null', 'undefined', 'true', 'false', 'enum', 'namespace', 'declare', 'as', 'keyof', 'readonly'],
  go: ['package', 'import', 'func', 'return', 'if', 'else', 'for', 'range', 'switch', 'case', 'break', 'continue', 'defer', 'go', 'chan', 'select', 'struct', 'interface', 'type', 'var', 'const', 'map', 'nil', 'true', 'false', 'make', 'append', 'len', 'cap', 'close', 'delete', 'copy', 'panic', 'recover'],
  rust: ['fn', 'let', 'mut', 'const', 'static', 'struct', 'enum', 'impl', 'trait', 'pub', 'use', 'mod', 'crate', 'self', 'super', 'where', 'for', 'while', 'loop', 'if', 'else', 'match', 'return', 'break', 'continue', 'async', 'await', 'move', 'ref', 'type', 'unsafe', 'extern', 'dyn', 'impl', 'true', 'false', 'Some', 'None', 'Ok', 'Err'],
  cpp: ['auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while', 'class', 'public', 'private', 'protected', 'virtual', 'override', 'final', 'namespace', 'using', 'template', 'typename', 'new', 'delete', 'this', 'throw', 'try', 'catch', 'true', 'false', 'nullptr'],
  c: ['auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while', 'include', 'define', 'ifdef', 'ifndef', 'endif', 'pragma'],
  ruby: ['class', 'module', 'def', 'end', 'if', 'elsif', 'else', 'unless', 'case', 'when', 'while', 'until', 'for', 'do', 'begin', 'rescue', 'ensure', 'raise', 'return', 'yield', 'block', 'proc', 'lambda', 'self', 'nil', 'true', 'false', 'and', 'or', 'not', 'in', 'require', 'include', 'extend', 'attr_accessor', 'attr_reader', 'attr_writer'],
};

const EXTENSION_MAP: Record<string, string> = {
  py: 'python',
  java: 'java',
  js: 'javascript',
  ts: 'typescript',
  go: 'go',
  rs: 'rust',
  c: 'c',
  cpp: 'cpp',
  cc: 'cpp',
  rb: 'ruby',
};

@Component({
  selector: 'app-code-preview',
  imports: [],
  template: `
    <div class="code-preview">
      <div class="code-header">
        <span class="filename">{{ filename() }}</span>
        @if (language()) {
          <span class="lang-badge">{{ language() }}</span>
        }
      </div>
      <pre class="code-block"><code [innerHTML]="highlightedCode()"></code></pre>
    </div>
  `,
  styleUrl: './code-preview.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CodePreview {
  code = input.required<string>();
  filename = input<string>('code');
  language = input<string>('');

  detectedLang = computed(() => {
    if (this.language()) return this.language();
    const ext = this.filename().split('.').pop()?.toLowerCase() ?? '';
    return EXTENSION_MAP[ext] ?? '';
  });

  keywords = computed(() => {
    const lang = this.detectedLang();
    return LANG_KEYWORDS[lang] ?? [];
  });

  highlightedCode = computed(() => {
    const code = this.code();
    const keywords = this.keywords();

    if (keywords.length === 0) {
      return this.escapeHtml(code);
    }

    const escaped = this.escapeHtml(code);
    const keywordPattern = new RegExp(`\\b(${keywords.join('|')})\\b`, 'g');

    return escaped
      .replace(/(\/\/.*$|#.*$)/gm, '<span class="code-comment">$1</span>')
      .replace(/("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"]*"|\'[^\']*\')/g, '<span class="code-string">$1</span>')
      .replace(keywordPattern, '<span class="code-keyword">$1</span>')
      .replace(/\b(\d+\.?\d*)\b/g, '<span class="code-number">$1</span>');
  });

  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
}
