# Fetch ECS Services and Tasks by VPC

# Usage
1) Clone the repo
```bash
git clone https://github.com/realjoshparker/aws-helpers.git
```

2) Navigate to the `fetch-by-vpc` directory and install the dependencies
```bash
cd aws-helpers/ecs/fetch-by-vpc
pip3 install -r requirements.txt
```

3) Run the script
```bash
python3 fetch-by-vpc.py
```

The script will ask for 2 inputs the VPC and region we are looking for resources in, provide it those and it'll do the rest. Once complete the service/task list can be printed out to the console or saved to a file. 