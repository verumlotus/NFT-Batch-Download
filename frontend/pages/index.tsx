import type { NextPage } from 'next'
import Head from 'next/head'
import Image from 'next/image'
import { useState } from 'react'
import styles from '../styles/Home.module.css'
import axios from "axios"
import Footer from '../components/Footer'

const SERVER_URL = process.env.NEXT_PUBLIC_SERVER_URL
console.log(`Server is ${SERVER_URL}`)

type ServerResponse = {
   s3Link: string,
   status: 'pending' | 'in-progress' | 'finished'
}

const Home: NextPage = () => {
  const [contractAddress, setContractAddress] = useState("");
  const [returnString, setReturnString] = useState("")
  const [s3BucketLink, setS3BucketLink] = useState("")

  async function processContractAddress() {
    const url = `${SERVER_URL}/collections/${contractAddress}`
    const raw_res = await axios.get(
      url
    )
    const server_res: ServerResponse = raw_res.data
    if (server_res.status == 'pending') {
      setReturnString(`A backend job has been kicked off to download the images for ${contractAddress}! Check
      back in a while for the S3 link (~2 min for the first batch of images)`)
    }
    else if (server_res.status == 'in-progress') {
      setReturnString(`Some images have been downloaded!`)
      setS3BucketLink(server_res.s3Link)
    }
    else if (server_res.status == 'finished') {
      setReturnString(`All images have been downloaded!`)
      setS3BucketLink(server_res.s3Link)
    }
  }

  return (
    <div className={styles.container}>
      <Head>
        <title>NFT Batch Download</title>
        <meta name="description" content="Batch download NFT collections" />
        <link rel="icon" type="image/png" sizes="16x16" href="/images/mona-lisa.png" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>
          NFT Batch Download
        </h1>

        <p className={styles.description}>
          Enter the contract address of an NFT Collection on Ethereum. Images for that collection will be uploaded to an S3 bucket for batch downloading.
        </p>

        <input
          placeholder={`<Contract Address Here>`}
          value={contractAddress}
          onChange={(e) => setContractAddress(e.target.value)}
          style={{"width": "60vw"}}
        />

        <button 
          onClick={processContractAddress}
          style={{"height": "6vh", "width": "16vw", "marginTop": "3vh"}}
        >
          Download to S3
        </button>

        <p>{returnString}</p>
        {s3BucketLink &&
          <p>View the images <a href={s3BucketLink} style={{color: "blue"}}>here</a></p>
        }
        <Footer/>

      </main>
    </div>
  )
}

export default Home