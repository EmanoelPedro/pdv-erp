#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::ffi::OsString;
use std::fs::read_dir;
use std::fs::{create_dir_all, OpenOptions};
use std::io::Write;
use std::net::TcpListener;
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;

use serde::Serialize;
use tauri::{AppHandle, Manager, State};

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct RuntimeConfig {
    api_base_url: String,
}

struct BackendProcess {
    child: Child,
    api_base_url: String,
    log_path: PathBuf,
}

#[derive(Default)]
struct BackendSupervisorState {
    process: Mutex<Option<BackendProcess>>,
}

fn append_supervisor_log(log_path: &PathBuf, message: &str) {
    if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(log_path) {
        let _ = writeln!(file, "[tauri-supervisor] {message}");
    }
}

fn resolve_app_data_dir(app: &AppHandle) -> Result<PathBuf, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|error| error.to_string())?;
    create_dir_all(&app_data_dir).map_err(|error| error.to_string())?;
    Ok(app_data_dir)
}

fn resolve_bundled_resource_roots(app: &AppHandle) -> Vec<PathBuf> {
    let mut roots = Vec::new();

    if let Ok(resource_dir) = app.path().resource_dir() {
        if resource_dir.is_dir() {
            roots.push(resource_dir);
        }
    }

    if let Ok(current_executable) = std::env::current_exe() {
        if let Some(executable_dir) = current_executable.parent() {
            let sibling_resources_dir = executable_dir.join("resources");
            if sibling_resources_dir.is_dir() {
                roots.push(sibling_resources_dir);
            }
        }

        if let Ok(canonical_executable) = current_executable.canonicalize() {
            if let Some(executable_dir) = canonical_executable.parent() {
                let sibling_resources_dir = executable_dir.join("resources");
                if sibling_resources_dir.is_dir() {
                    roots.push(sibling_resources_dir);
                }
            }
        }
    }

    if cfg!(target_os = "linux") {
        if let Ok(entries) = read_dir("/usr/lib") {
            for entry in entries.flatten() {
                let candidate = entry.path().join("resources");
                if candidate.is_dir() {
                    roots.push(candidate);
                }
            }
        }
    }

    roots.sort();
    roots.dedup();

    roots
}

fn resolve_backend_workdir(app: &AppHandle) -> Result<PathBuf, String> {
    if let Ok(path) = std::env::var("PDV_BACKEND_WORKDIR") {
        return Ok(PathBuf::from(path));
    }

    if cfg!(debug_assertions) {
        let development_backend_dir =
            PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../backend");
        if development_backend_dir.is_dir() {
            return development_backend_dir
                .canonicalize()
                .map_err(|error| error.to_string());
        }
    }

    for resource_root in resolve_bundled_resource_roots(app) {
        let bundled_backend_dir = resource_root.join("backend");
        if bundled_backend_dir.is_dir() {
            return Ok(bundled_backend_dir);
        }
    }

    Err(String::from(
        "Local backend directory could not be resolved for the desktop runtime.",
    ))
}

fn resolve_python_command(app: &AppHandle) -> OsString {
    if let Ok(path) = std::env::var("PDV_BACKEND_PYTHON") {
        return OsString::from(path);
    }

    if cfg!(debug_assertions) {
        let development_runtime_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("resources")
            .join("python");
        let development_candidates = if cfg!(target_os = "windows") {
            vec![
                development_runtime_dir.join("Scripts").join("python.exe"),
                development_runtime_dir.join("python.exe"),
            ]
        } else {
            vec![
                development_runtime_dir.join("bin").join("python3"),
                development_runtime_dir.join("bin").join("python"),
            ]
        };

        for candidate in development_candidates {
            if candidate.is_file() {
                return candidate.into_os_string();
            }
        }
    }

    for resource_dir in resolve_bundled_resource_roots(app) {
        let bundled_candidates = if cfg!(target_os = "windows") {
            vec![
                resource_dir
                    .join("python")
                    .join("Scripts")
                    .join("python.exe"),
                resource_dir.join("python").join("python.exe"),
            ]
        } else {
            vec![
                resource_dir.join("python").join("bin").join("python3"),
                resource_dir.join("python").join("bin").join("python"),
            ]
        };

        for candidate in bundled_candidates {
            if candidate.is_file() {
                return candidate.into_os_string();
            }
        }
    }

    if cfg!(target_os = "windows") {
        OsString::from("python")
    } else {
        OsString::from("python3")
    }
}

fn find_available_port() -> Result<u16, String> {
    let listener = TcpListener::bind("127.0.0.1:0").map_err(|error| error.to_string())?;
    let port = listener
        .local_addr()
        .map_err(|error| error.to_string())?
        .port();
    drop(listener);
    Ok(port)
}

fn spawn_backend_process(app: &AppHandle) -> Result<BackendProcess, String> {
    let app_data_dir = resolve_app_data_dir(app)?;
    let logs_dir = app_data_dir.join("logs");
    create_dir_all(&logs_dir).map_err(|error| error.to_string())?;

    let log_path = logs_dir.join("backend.log");
    let stdout_log = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_path)
        .map_err(|error| error.to_string())?;
    let stderr_log = stdout_log.try_clone().map_err(|error| error.to_string())?;

    let backend_dir = resolve_backend_workdir(app)?;
    let python_command = resolve_python_command(app);
    let port = find_available_port()?;
    let api_base_url = format!("http://127.0.0.1:{port}");

    append_supervisor_log(
        &log_path,
        &format!(
            "starting backend with {:?} in {} on {}",
            python_command,
            backend_dir.display(),
            api_base_url
        ),
    );

    let child = Command::new(&python_command)
        .current_dir(&backend_dir)
        .arg("-m")
        .arg("app.local_server")
        .env("ENVIRONMENT", "desktop")
        .env("DATA_DIR", &app_data_dir)
        .env("API_HOST", "127.0.0.1")
        .env("API_PORT", port.to_string())
        .env("PYTHONUNBUFFERED", "1")
        .env("PYTHONDONTWRITEBYTECODE", "1")
        .stdin(Stdio::null())
        .stdout(Stdio::from(stdout_log))
        .stderr(Stdio::from(stderr_log))
        .spawn()
        .map_err(|error| format!("Failed to start local backend: {error}"))?;

    Ok(BackendProcess {
        child,
        api_base_url,
        log_path,
    })
}

fn ensure_backend_running(
    app: &AppHandle,
    state: &BackendSupervisorState,
) -> Result<RuntimeConfig, String> {
    let mut process_guard = state
        .process
        .lock()
        .map_err(|_| String::from("Backend supervisor state is unavailable."))?;

    if let Some(process) = process_guard.as_mut() {
        match process.child.try_wait() {
            Ok(None) => {
                return Ok(RuntimeConfig {
                    api_base_url: process.api_base_url.clone(),
                });
            }
            Ok(Some(status)) => {
                append_supervisor_log(
                    &process.log_path,
                    &format!("backend exited unexpectedly with status {status}"),
                );
                *process_guard = None;
            }
            Err(error) => {
                append_supervisor_log(
                    &process.log_path,
                    &format!("backend state check failed: {error}"),
                );
                *process_guard = None;
            }
        }
    }

    let backend_process = spawn_backend_process(app)?;
    let config = RuntimeConfig {
        api_base_url: backend_process.api_base_url.clone(),
    };

    *process_guard = Some(backend_process);
    Ok(config)
}

fn stop_backend_process(state: &BackendSupervisorState) {
    let mut process_guard = match state.process.lock() {
        Ok(guard) => guard,
        Err(_) => return,
    };

    if let Some(mut process) = process_guard.take() {
        append_supervisor_log(&process.log_path, "stopping backend process");
        let _ = process.child.kill();
        let _ = process.child.wait();
    }
}

#[tauri::command]
fn get_runtime_config(
    app: AppHandle,
    state: State<BackendSupervisorState>,
) -> Result<RuntimeConfig, String> {
    ensure_backend_running(&app, &state)
}

fn main() {
    let app = tauri::Builder::default()
        .manage(BackendSupervisorState::default())
        .setup(|app| {
            let app_handle = app.handle().clone();
            let state = app.state::<BackendSupervisorState>();

            if let Err(error) = ensure_backend_running(&app_handle, &state) {
                eprintln!("failed to start local backend during setup: {error}");
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_runtime_config])
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    app.run(|app_handle, event| {
        if matches!(event, tauri::RunEvent::Exit) {
            let state = app_handle.state::<BackendSupervisorState>();
            stop_backend_process(&state);
        }
    })
}
