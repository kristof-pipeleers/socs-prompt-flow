import os
import subprocess
from datetime import datetime

def replace_company_name(batch_run_template, company_name, run_name):
    # Use f-string to directly substitute the variables
    return batch_run_template.replace('${company_name}', f'"{company_name}"').replace('${run_name}', f'"{run_name}"')

def main():
    # Path to the create_run.yaml file
    create_run_yaml = "batch_run_create.yaml"

    # Read the list of company names from the companies.txt file
    with open("companies.txt", "r") as file:
        company_names = file.read().splitlines()

    # Read the template batch_run.jsonl file
    with open("batch_run.jsonl", "r") as file:
        batch_run_template = file.read()

    venv_activate_script = os.path.join("venv", "Scripts", "activate")


    # Iterate through each company name
    for company_name in company_names:

        run_name = f"run_{company_name}"
        
        # Replace the placeholders in the batch_run.jsonl file
        batch_run_content = replace_company_name(batch_run_template, company_name, run_name)

        # Write the updated batch_run.jsonl content to a temporary file
        temp_batch_run_path = "temp_batch_run.jsonl"
        with open(temp_batch_run_path, "w") as temp_file:
            temp_file.write(batch_run_content)

        '''activate_cmd = f".{venv_activate_script}"  # Use "." for sourcing in PowerShell
        print(activate_cmd)
        subprocess.run(activate_cmd, shell=True, check=True)'''
        
        # Run the create_run.yaml script with the updated batch_run.jsonl file
        command = [
            "python",
            "-m",
            "promptflow._cli._pf.entry",
            "run",
            "create",
            "--stream",
            "--file",
            create_run_yaml,
        ]

        print(command)

        try:
            # Execute the command
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running create_run.yaml for {company_name}: {e}")

        # Remove the temporary batch_run.jsonl file
        os.remove(temp_batch_run_path)

if __name__ == "__main__":
    main()
