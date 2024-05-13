import subprocess
import os
from crontab import CronTab
import venv

def create_venv():
    """Creates and activates a Python virtual environment."""
    subprocess.run(["pip", "install", "virtualenv"])
    venv_dir = "ooni_env"  # Name of the virtual environment directory
    venv.create(venv_dir, with_pip=True)  # Create the virtual environment
    
    # Activate the virtual environment
    if os.name == 'nt':  # Windows
        activate_script = os.path.join(venv_dir, 'Scripts', 'activate')
        subprocess.run(['cmd.exe', '/c', activate_script])
    else:  # macOS/Linux
        activate_script = os.path.join(venv_dir, 'bin', 'activate')
        subprocess.run(['source', activate_script])

def install_dependencies():
    """Installs required Python packages."""
    try:
        subprocess.run([
                   "pip",
                   "install",
                   "boto3",
                   "cryptography",
                   "requests",
                   "python-dotenv",
                   "ratelimit",
                   "crontab",
                   "gzip",
                   "json"
           ])
        print("Dependencies installed successfully!")
    except Exception as e:
        print(f"Error installing dependencies: {e}")

def guidance_for_s3cmd_configuration():
    """Asks the user if they want to configure s3cmd and guides them through it."""
    configure = input("Do you want to configure s3cmd to download OONI data from S3? (yes/no): ")
    if configure.lower() == "yes":
        try:
            # Instructions to configure s3cmd (you'll need to fill this in)
            print("1. Install s3cmd: pip install s3cmd")
            print("2. Run 's3cmd --configure' and follow the prompts to set up your AWS credentials.")
        except Exception as e:
            print(f"Error configuring s3cmd: {e}")

def create_cron_job():
    """Creates a cron job to run the main script periodically."""
    cron = CronTab(user=True)
    job = cron.new(command=f"source /path/to/your/venv/bin/activate; python /path/to/your/script/main.py")

    schedule_input = input("Enter cron schedule (e.g., '0 0 * * *' for daily at midnight): ")
    job.setall(schedule_input)
    cron.write()
    print("Cron job created successfully!")


if __name__ == "__main__":
    install_dependencies()
    guidance_for_s3cmd_configuration()
    create_cron_job()
    print("Setup complete! Your script is scheduled to run periodically.")
