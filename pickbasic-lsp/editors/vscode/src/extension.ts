import { ExtensionContext, workspace } from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
} from "vscode-languageclient/node";

let client: LanguageClient | undefined;

export function activate(context: ExtensionContext) {
  const pythonPath = workspace
    .getConfiguration("pickbasic")
    .get<string>("server.pythonPath", "python3");

  const serverOptions: ServerOptions = {
    command: pythonPath,
    args: ["-m", "pickbasic_lsp"],
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: "file", language: "pickbasic" }],
    synchronize: {
      fileEvents: workspace.createFileSystemWatcher(
        "**/*.{bp,b,bas,basic}"
      ),
    },
  };

  client = new LanguageClient(
    "pickbasicLanguageServer",
    "Pick BASIC Language Server",
    serverOptions,
    clientOptions
  );

  client.start();
}

export function deactivate(): Thenable<void> | undefined {
  return client?.stop();
}
