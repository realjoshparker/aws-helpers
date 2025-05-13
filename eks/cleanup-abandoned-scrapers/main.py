import boto3
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Find ECS tasks by their private IP address')
    parser.add_argument('-r', '--region', required=False, help='Specify an AWS region to search in, defaults to whatever is configured in ~/.aws/config')
    parser.add_argument('-f', '--force', required=False, default=False, help='If passed any scrapers found abandonded will be deleted automatically')
    return parser.parse_args()

def fetch_scrapers(region):
    amp = boto3.client('amp', region_name=region)
    
    scraper_list = amp.list_scrapers()
    return scraper_list['scrapers']
    
def fetch_clusters(region):
    eks = boto3.client('eks', region_name=region)
    
    cluster_list = eks.list_clusters()['clusters']

    return cluster_list
    
def find_abandoned_scrapers(scraper_list, cluster_list):
    abandonded_scrapers = []
    
    for scraper in scraper_list:
        scraperCluster = scraper['source']['eksConfiguration']['clusterArn'].split('/')[1]
        if scraperCluster not in cluster_list:
            print(f"Scraper {scraper['scraperId']} abandoned, adding to list...")
            abandonded_scrapers.append(scraper['scraperId'])
        else:
            pass
            #print(f"Scraper {scraper['scraperId']} is not abandoned, belongs to {scraperCluster}")
            
    return abandonded_scrapers
    
def delete_scrapers(scrapers_list, region):
    amp = boto3.client('amp', region_name=region)
    
    for scraper in scrapers_list:
        amp.delete_scraper(scraperId=scraper)
        
    print("Delete signal sent")

def main():
    deleteScrapers = False
    args = parse_arguments()
    
    scrapers = fetch_scrapers(args.region)
    clusters = fetch_clusters(args.region)
    
    abandoned_scrapers = find_abandoned_scrapers(scrapers, clusters)
    if abandoned_scrapers:
        if args.force:
            deleteScrapers=True
        else:
            print("\nAbandoned Scrapers\n--------------------")
            for scraper in abandoned_scrapers:
                print(f"- {scraper}")
            print("--------------------\n")
            response = input("We found the abandoned scrapers above, would you like to delete them? (yes or y to delete): ")
            if response in ["yes", "y"]: 
                delete_scrapers(abandoned_scrapers, args.region)
            else:
                print("Not deleting scrapers")
    else:
        print("No abandoned scrapers found, nothing to delete")
        
    if deleteScrapers:
        delete_scrapers(abandoned_scrapers, args.region)
    
if __name__ == "__main__":
    main()