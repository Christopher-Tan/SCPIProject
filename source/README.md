# SCPIProject

## Setup Instructions

### 1. Setting Up the Environment (Server and Client)

1. **Clone the Repository**  
    Clone this repository to your local machine:
    ```bash
    git clone https://github.com/Christopher-Tan/SCPIProject.git
    cd SCPIProject
    ```

2. **Create a Virtual Environment (Optional but Highly Recommended)**  
    To isolate dependencies and avoid conflicts, create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Required Dependencies**  
    Install the required dependencies from the `requirements.txt` file:
    ```bash
    pip install -r source/requirements.txt
    ```

4. **Install the Custom PyMeasure Library**  
    We use a custom version of PyMeasure with additional instruments. You have two options to integrate this:
    #### Option 1: Modify Your Existing PyMeasure Library
        - Copy the instruments from our `source/instruments` folder.
        - Paste them into your local `pymeasure/instruments` folder.
        - To locate your existing PyMeasure installation, you can use the following Python command:
        ```python
        import pymeasure
        print(pymeasure.__file__)
        ```
        - This will print the path to the PyMeasure library on your system.
        - Navigate to the `instruments` folder within that path and paste the copied instruments there.  
    #### Option 2: Use Our Custom PyMeasure Version
        - Install our custom version directly:
        ```bash
        pip install -e source/pymeasure
        ```
        - **Warning:** This will overwrite any local changes in your existing PyMeasure library. If you have a custom PyMeasure setup, back up your changes before proceeding.

### 2. Automatically Start the Server on a Raspberry Pi

To ensure the server starts automatically when the Raspberry Pi boots, follow these steps:

1. **Edit /etc/rc.local**  
Edit this file to look as follows
```bash
#!/bin/bash
# Replace the following placeholders with your specific details:
# {env} - Path to your virtual environment's Python binary
# {project_location} - Path to your SCPIProject folder

sudo {env}/python3 {project_location}/source/SCPIServer.py &
```

Remember to give the file the following permissions
```
sudo chmod 755 /etc/rc.local
```

### Example:
If your virtual environment is located at `/home/pi/venv` and your project is in `/home/pi/SCPIProject`, the script would look like this:
```bash
#!/bin/bash
sudo /home/pi/venv/bin/python3 /home/pi/SCPIProject/source/SCPIServer.py &
```
If this is indeed your set up, this is a standard default you can use the following script to do all of the above

```bash
echo -e '#!/bin/bash\nsudo /home/pi/venv/bin/python3 /home/pi/SCPIProject/source/SCPIServer.py &' | sudo tee /etc/rc.local
sudo chmod 755 /etc/rc.local
```
