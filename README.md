# NFT-Batch-Download
Batch upload images from an NFT collection to AWS S3, and download them locally if desired.

# Background
On-chain contracts only contain a reference to the NFT image & metadata. The actual content is stored on [IPFS](https://ipfs.io/) or a 
Web Server. It's a [misconception](https://docs.ipfs.io/concepts/persistence/) that data stored on IPFS is permanent – many NFT collections use 3rd party [pinning services](https://docs.ipfs.io/how-to/work-with-pinning-services/) to make their content available. If the data is no longer pinned, it may be lost forever. For web servers, if the server is shutdown (forgetting to pay the bill, malicious intent, etc.) images & metadata are inaccessible and your NFT points to a 404 link. In fact, for Web Servers, the developers can change the content at the URL at any moment (see [this](https://metaversal.banklesshq.com/p/racoon-rugged-society) example of all NFT images in a collection being replaced)

The service in this repo accepts an Ethereum contract address corresponding to an NFT collection. It then fetches the image URIs and 
proceeds to download them and upload them to S3 in small batches. The intention is for users to download images locally in case
images become unavailable. For images stored on IPFS, in the event that images are no longer pinned to IPFS, users can find the IPFS hash of 
images they have locally. These could be checked against historical blockchain data to come to community consensus on which images were
actually included in the collection (and what tokenID they correspond to).

# Architecture
Our server is run in a [Docker container](https://www.docker.com/resources/what-container/) that is running an instance of the [Uvicorn](https://www.uvicorn.org/) Web server with [FastAPI](https://fastapi.tiangolo.com/). The downloading of metadata & images is a computationally intensive task that is best performed asynchronously, so our architecture includes a [task queue](https://www.fullstackpython.com/task-queues.html) to handle requests. We use Python's wonderful [Celery](https://docs.celeryq.dev/en/stable/index.html) library to make the process simpler. The server sends tasks to [Redis](https://redis.io/) (our choice for a message broker), and a fleet of celery workers (run as docker containers) pull tasks from the queue. Celery workers fetch the NFT Image URIs from a node provider ([Alchemy](https://www.alchemy.com/) in our case) and proceed to download the images (via an [IPFS Gateway](https://docs.ipfs.io/concepts/ipfs-gateway/) if the images are stored on IPFS, or else directly requesting the image from the Web Server). Images are uploaded to a public [AWS S3](https://aws.amazon.com/s3/) bucket in batches, where they can then be downloaded by any user. [LogTail](https://betterstack.com/logtail) is our log management service that aggregates logs from nodes across our system. 

<img width="924" alt="image" src="https://user-images.githubusercontent.com/97858468/178121118-a19356eb-fcf1-42f9-8c52-9c90bc927c44.png">

# Hosting this service
Originally, the intention was to launch this service and allow users to batch upload images to AWS S3 and then download them. Unfortunately, the costs of hosting this infrastructure was too high for a college student. In particular, the [data egress cost](https://aws.amazon.com/s3/pricing/) from an S3 bucket made the cost prohibitvely high even if this service reached moderate adoption. Data egress is priced at $0.09/GB: assuming an average image size of 300KB and an average collection size of 10,000, each collection would be ~3GB with all images included. With 30 NFT collections of interest, and 100 users downloading all the images, we'd have $0.09/GB x 3GB x 30 x 100 = $810. This is only the S3 cost, and excludes other infrastructure costs. Mostly likely this service would have reached far lower numbers of users, but since AWS doesn't have a way to cap billing (only a way to set alerts), I didn't want to wake up to a large bill!






