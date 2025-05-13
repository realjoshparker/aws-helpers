# Cleanup abandoned EKS scrapers
If you've deleted an EKS cluster without cleaning up the underlying managed scraper you would be unable to delete the VPC the cluster ran in, and moreover you will continue to be billed for it.

This script helps to automate the cleanup process, it will get a list of EKS clusters as well as a list of scrapers in your account/region. From there it will compare the scrapers owner references to the list of clusters and will add all scrapers without a corresponding cluster to a list. Finally it'll print those and ask if we should remove them. Optionally you can pass the `--force` flag to force remove any found scrapers. 

# Usage
1) Clone the repo
```bash
git clone https://github.com/realjoshparker/aws-helpers.git
```

2) Navigate to the `fetch-by-vpc` directory and install the dependencies
```bash
cd aws-helpers/eks/cleanup-abandoned-scrapers
pip3 install -r requirements.txt
```

3) Run the script
```bash
python3 main.py
```

By default it will use the region defined in your `~/.aws/config` file. You can pass `--region` to specify a different region.

## Flags
| Flag | Shorthand | Default | Description |
| -- | -- | -- | -- |
| `--region` | `-r` | `us-east-1` | Specifies the region to look for abandoned scrapers in |
| `--force` | `-f` | False | Force delete any found abandoned scrapers |