import os
import time
import shutil
from playwright.sync_api import sync_playwright

def record():
    # Ensure docs/assets directory exists
    os.makedirs("docs/assets", exist_ok=True)
    temp_dir = "docs/assets/temp_videos"
    os.makedirs(temp_dir, exist_ok=True)
    
    with sync_playwright() as p:
        # Launch Chromium headless
        browser = p.chromium.launch(headless=True)
        
        # Create browser context with 1280x720 video recording enabled
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=temp_dir
        )
        
        page = context.new_page()
        
        print("1. Opening Web GUI Landing page...")
        page.goto("http://localhost:3000")
        page.wait_for_timeout(2000)
        
        print("2. Toggling Register Account Tab...")
        page.click("#tab-register")
        page.wait_for_timeout(1000)
        
        print("3. Entering registration credentials...")
        page.fill("#register-email", "demo_user@example.com")
        page.fill("#register-password", "password123")
        page.wait_for_timeout(1500)
        
        print("4. Registering account...")
        page.click("#form-register button[type='submit']")
        page.wait_for_timeout(3000) # wait for signup complete toast
        
        print("5. Entering sign in credentials...")
        page.fill("#login-email", "demo_user@example.com")
        page.fill("#login-password", "password123")
        page.wait_for_timeout(1500)
        
        print("6. Signing in...")
        page.click("#form-login button[type='submit']")
        page.wait_for_timeout(3000) # wait for dashboard render
        
        print("7. Launching Create Project modal...")
        page.click("#btn-new-project")
        page.wait_for_timeout(1000)
        
        print("8. Filling project details...")
        page.fill("#project-name-input", "Beta Release Project")
        page.fill("#project-desc-input", "Tracking launch checklist items.")
        page.wait_for_timeout(1500)
        page.click("#btn-submit-project-dialog")
        page.wait_for_timeout(2000)
        
        print("9. Selecting the project card...")
        page.click(".project-item:has-text('Beta Release Project')")
        page.wait_for_timeout(2000)
        
        print("10. Launching Add Task modal...")
        page.click("#btn-new-task")
        page.wait_for_timeout(1000)
        
        print("11. Filling task details...")
        page.fill("#task-title-input", "Configure CI Pipeline")
        page.fill("#task-desc-input", "Set up github actions yml workflows.")
        page.wait_for_timeout(1500)
        page.click("#btn-submit-task-dialog")
        page.wait_for_timeout(2000)
        
        print("12. Toggling task status to InProgress...")
        page.click(".btn-toggle-status")
        page.wait_for_timeout(2500)
        
        print("13. Logging out from profile...")
        page.click("#btn-logout")
        page.wait_for_timeout(2000)
        
        # Extract recording path and close connections
        video_path = page.video.path()
        context.close()
        browser.close()
        
        final_video_path = "docs/assets/onboarding_walkthrough.webm"
        if os.path.exists(video_path):
            if os.path.exists(final_video_path):
                os.remove(final_video_path)
            shutil.move(video_path, final_video_path)
            print(f"SUCCESS: Walkthrough video recorded and saved to {final_video_path}")
            
            # Cleanup temp directory
            shutil.rmtree(temp_dir)
        else:
            print("ERROR: Walkthrough video path not found.")

if __name__ == "__main__":
    record()
