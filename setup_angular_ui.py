guards",
        "src/app/directives",
        "src/assets/images",
        "src/assets/icons",
        "src/assets/docs",
        "src/assets/illustrations",
        "src/environments"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created {dir_path}")
    
    # Step 5: Create Angular configuration files
    print("\n⚙️ Step 5: Creating configuration files...")
    
    # angular.json
    angular_config = {
        "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
        "version": 1,
        "newProjectRoot": "projects",
        "projects": {
            "legacy-codebase-assistant": {
                "projectType": "application",
                "schematics": {
                    "@schematics/angular:component": {
                        "style": "scss"
                    }
                },
                "root": "",
                "sourceRoot": "src",
                "prefix": "app",
                "architect": {
                    "build": {
                        "builder": "@angular-devkit/build-angular:browser",
                        "options": {
                            "outputPath": "dist",
                            "index": "src/index.html",
                            "main": "src/main.ts",
                            "polyfills": ["zone.js"],
                            "tsConfig": "tsconfig.app.json",
                            "assets": ["src/favicon.ico", "src/assets"],
                            "styles": [
                                "@angular/material/prebuilt-themes/indigo-pink.css",
                                "src/styles.scss"
                            ],
                            "scripts": []
                        },
                        "configurations": {
                            "production": {
                                "budgets": [
                                    {
                                        "type": "initial",
                                        "maximumWarning": "2mb",
                                        "maximumError": "5mb"
                                    }
                                ],
                                "outputHashing": "all",
                                "optimization": true,
                                "sourceMap": false,
                                "namedChunks": false,
                                "extractLicenses": true,
                                "vendorChunk": false,
                                "buildOptimizer": true
                            },
                            "development": {
                                "buildOptimizer": false,
                                "optimization": false,
                                "vendorChunk": true,
                                "extractLicenses": false,
                                "sourceMap": true,
                                "namedChunks": true
                            }
                        },
                        "defaultConfiguration": "production"
                    },
                    "serve": {
                        "builder": "@angular-devkit/build-angular:dev-server",
                        "configurations": {
                            "production": {
                                "buildTarget": "legacy-codebase-assistant:build:production"
                            },
                            "development": {
                                "buildTarget": "legacy-codebase-assistant:build:development"
                            }
                        },
                        "defaultConfiguration": "development",
                        "options": {
                            "proxyConfig": "proxy.conf.json"
                        }
                    }
                }
            }
        }
    }
    
    with open("angular.json", "w") as f:
        json.dump(angular_config, f, indent=2)
    print("  ✅ Created angular.json")
    
    # tsconfig.json
    tsconfig = {
        "compileOnSave": False,
        "compilerOptions": {
            "baseUrl": "./",
            "outDir": "./dist/out-tsc",
            "forceConsistentCasingInFileNames": True,
            "strict": True,
            "noImplicitOverride": True,
            "noPropertyAccessFromIndexSignature": True,
            "noImplicitReturns": True,
            "noFallthroughCasesInSwitch": True,
            "sourceMap": True,
            "declaration": False,
            "downlevelIteration": True,
            "experimentalDecorators": True,
            "moduleResolution": "node",
            "importHelpers": True,
            "target": "ES2022",
            "module": "ES2022",
            "useDefineForClassFields": False,
            "lib": ["ES2022", "dom"]
        },
        "angularCompilerOptions": {
            "enableI18nLegacyMessageIdFormat": False,
            "strictInjectionParameters": True,
            "strictInputAccessModifiers": True,
            "strictTemplates": True
        }
    }
    
    with open("tsconfig.json", "w") as f:
        json.dump(tsconfig, f, indent=2)
    print("  ✅ Created tsconfig.json")
    
    # proxy.conf.json for API calls
    proxy_config = {
        "/api": {
            "target": "http://localhost:8000",
            "secure": False,
            "changeOrigin": True,
            "logLevel": "debug"
        },
        "/ws": {
            "target": "ws://localhost:8000",
            "secure": False,
            "ws": True
        }
    }
    
    with open("proxy.conf.json", "w") as f:
        json.dump(proxy_config, f, indent=2)
    print("  ✅ Created proxy.conf.json")
    
    # Step 6: Create main application files
    print("\n📝 Step 6: Creating main application files...")
    
    # index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Legacy Codebase Assistant - AI-Powered Migration Intelligence</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <link rel="preconnect" href="https://fonts.gstatic.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
</head>
<body class="mat-typography">
  <app-root>
    <div class="loading-container">
      <div class="loader">
        <div class="loader-inner"></div>
      </div>
      <h2>Legacy Codebase Assistant</h2>
      <p>Initializing AI-powered analysis...</p>
    </div>
  </app-root>
  <style>
    .loading-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-family: 'Inter', sans-serif;
    }
    .loader {
      width: 60px;
      height: 60px;
      position: relative;
      margin-bottom: 20px;
    }
    .loader-inner {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      border: 3px solid rgba(255, 255, 255, 0.3);
      border-top-color: white;
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .loading-container h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
    }
    .loading-container p {
      margin: 8px 0 0;
      opacity: 0.8;
    }
  </style>
</body>
</html>"""
    
    with open("src/index.html", "w") as f:
        f.write(index_html)
    print("  ✅ Created index.html")
    
    # styles.scss
    styles_scss = """/* Global Styles */
@import '@angular/material/prebuilt-themes/indigo-pink.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  background: #f5f5f7;
}

/* Material Theme Customization */
.mat-toolbar {
  font-family: inherit;
}

.mat-card {
  border-radius: 12px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
  transition: all 0.3s ease;
}

.mat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12) !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.3s ease;
}

.slide-in-up {
  animation: slideInUp 0.4s ease;
}

/* Utility Classes */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.mt-1 { margin-top: 8px; }
.mt-2 { margin-top: 16px; }
.mt-3 { margin-top: 24px; }
.mt-4 { margin-top: 32px; }

.mb-1 { margin-bottom: 8px; }
.mb-2 { margin-bottom: 16px; }
.mb-3 { margin-bottom: 24px; }
.mb-4 { margin-bottom: 32px; }

.p-1 { padding: 8px; }
.p-2 { padding: 16px; }
.p-3 { padding: 24px; }
.p-4 { padding: 32px; }

/* Dark Theme */
.dark-theme {
  background: #1a1a2e;
  color: #e0e0e0;
}

.dark-theme .mat-card {
  background: #2d2d44;
  color: #e0e0e0;
}

.dark-theme .mat-toolbar {
  background: #2d2d44;
  color: #e0e0e0;
}

.dark-theme ::-webkit-scrollbar-track {
  background: #2d2d44;
}

.dark-theme ::-webkit-scrollbar-thumb {
  background: #555;
}

/* Code Highlighting */
pre {
  background: #f4f4f4;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.dark-theme pre {
  background: #1e1e2e;
  color: #e0e0e0;
}

code {
  background: rgba(103, 58, 183, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 0.9em;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hide-mobile {
    display: none !important;
  }
}

@media (min-width: 769px) {
  .show-mobile {
    display: none !important;
  }
}"""
    
    with open("src/styles.scss", "w") as f:
        f.write(styles_scss)
    print("  ✅ Created styles.scss")
    
    # main.ts
    main_ts = """import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .catch(err => console.error(err));"""
    
    with open("src/main.ts", "w") as f:
        f.write(main_ts)
    print("  ✅ Created main.ts")
    
    # environments/environment.ts
    environment_ts = """export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  wsUrl: 'ws://localhost:8000/ws',
  version: '2.0.0',
  features: {
    websocket: true,
    export: true,
    darkMode: true,
    analytics: true
  }
};"""
    
    with open("src/environments/environment.ts", "w") as f:
        f.write(environment_ts)
    print("  ✅ Created environment.ts")
    
    # environment.prod.ts
    environment_prod_ts = """export const environment = {
  production: true,
  apiUrl: '/api',
  wsUrl: '/ws',
  version: '2.0.0',
  features: {
    websocket: true,
    export: true,
    darkMode: true,
    analytics: true
  }
};"""
    
    with open("src/environments/environment.prod.ts", "w") as f:
        f.write(environment_prod_ts)
    print("  ✅ Created environment.prod.ts")
    
    print("\n✨ Angular UI setup complete!")
    print("\n📋 Next steps:")
    print("  1. Start the backend API: python api/enhanced_strands_app.py")
    print("  2. Start the Angular dev server: npm start")
    print("  3. Open your browser to: http://localhost:4200")
    print("\n🚀 Your enterprise Angular UI is ready!")
    
    return True

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)  # Go to project root
    success = setup_angular_project()
    
    if success:
        print("\n" + "="*60)
        print("🎉 SUCCESS! Enterprise Angular UI is configured")
        print("="*60)
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)