# TabPyMigrate

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/your_username/TabPyMigrate/blob/main/LICENSE)

> Short project description

TabPyMigrate is a tool to migrate your Tableau Flow, Datasources, Workbooks from one server to another easily.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation


### Prerequisites

- Python 3.6+
- Other dependencies

```bash
# Clone the repository
git clone https://github.com/codespg/TabPyMigrate.git

# Navigate to the project directory
cd TabPyMigrate

# Install the required packages
pip install -r requirements.txt
```

## Usage
Update config.py for source and target server and Tag the objects in Source Server
```
cd tabpymigrate
python tabpymigrate.py
```
Option2: Provide all required information and run in cli.
```
cd tabpymigrate
python tabpymigrate.py -action DOWNLOAD -source_server_name yourservername -source_username username -source_password password -tag_name tag_name -filesystem_path filesystem_path
```
