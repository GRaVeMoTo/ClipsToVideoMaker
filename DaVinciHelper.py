import wmi, time, win32process, win32gui, win32con
from pywinauto import Application

def RunDaVinciResolveScript(ScriptName):
    """Attempt to trigger a Workspace -> Scripts -> Comp -> <ScriptName> menu item in DaVinci Resolve.
    """


    # Find a top-level window for this PID
    def _find_window_for_process_name(process_name):
        """Return (pid, hwnd) for the first top-level window that belongs to a process named process_name."""
        try:
            c = wmi.WMI()
            procs = c.Win32_Process(Name=process_name)
        except Exception:
            return None, None
    
        for p in procs:
            try:
                pid = int(p.ProcessId)
            except Exception:
                continue
    
            hwnds = []
            def _cb(hwnd, lparam):
                try:
                    if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                        _, wpid = win32process.GetWindowThreadProcessId(hwnd)
                        if wpid == pid:
                            hwnds.append(hwnd)
                except Exception:
                    pass
                return True
    
            win32gui.EnumWindows(_cb, None)
            if hwnds:
                return pid, hwnds[0]
    
        return None, None

    pid, hwnd = _find_window_for_process_name("Resolve.exe")
    if not hwnd or not pid:
        print("Could not find Resolve window for process 'Resolve.exe'")
        return False
    
    if not hwnd:
        print("Could not find Resolve window for PID", pid)
        return False

    # Bring Resolve to foreground
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
    except Exception as e:
        print("Could not focus Resolve window:", e)

    # Try pywinauto first (more reliable if available)
    try:
        app = Application(backend='uia').connect(process=pid)
        win = app.window(handle=hwnd)
        menu_path = "Workspace->Scripts->Comp->Title" 
        try:
            win.menu_select(menu_path)
            print(f"Invoked {menu_path}")
            return True
        except Exception as e:
            # Some apps don't expose standard menus; fall back
            print("pywinauto menu_select failed, falling back:", e)
    except Exception as e:
        # pywinauto not available or failed to attach
        #print("pywinauto not available:", e)
        pass

if __name__ == "__main__":

    #RunDaVinciResolveScript("Title")
    from pywinauto import Desktop
    menu = Desktop(backend='uia').window(title_re=".*DaVinci Resolve.*")
    print("Bringing DaVinci Resolve to foreground...")
    menu.set_focus()
    print("focused.")
    wkps = menu.child_window(title="Workspace", control_type="MenuItem")
    print("Menu bar visible.")
    wkps.wait('visible', timeout=5)
    wkps.click()
    time.sleep(0.2)
    print("Workspace menu visible.")
    wkps.dump_tree(filename="workspace_menu.txt", depth=4)
    sc = wkps.child_window(title="Scripts", control_type="MenuItem")
    sc.wait('visible', timeout=5)
    time.sleep(0.2)

    print("Done")
