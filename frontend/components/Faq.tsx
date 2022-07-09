import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Link } from '@mui/material';


export default function Faq() {
  return (
    <div style={{padding: "0 0 0 0"}}>
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
        >
          <Typography>Why would we want to download NFT Images?</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant={"body1"}>
            On-chain contracts only contain a reference to the NFT image & metadata. The actual content is stored on IPFS or a 
            Web Server (e.g. for Crypto Coven & Milady). It&apos;s a misconception that data stored on IPFS is permanent – many NFT collections use 3rd party pinning
            services to make their content available. If the data is no longer pinned, it may be lost forever. For web servers, if the 
            server is shutdown (forgetting to pay the bill, malicious intent, etc.) images & metadata are inaccessible and your NFT points
            to a 404 link. The IPFS hash of images stored locally can be checked against historical blockchain data to verify an image was
            part of an NFT collection.
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
        >
          <Typography>What does this website do?</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant={"body1"}>
            This website accepts an Ethereum contract address corresponding to an NFT collection. It then fetches the image URIs and 
            proceeds to download them and upload them to S3 in small batches. The intention is for users to download images locally in case
            images become unavailable. For images stored on IPFS, in the event that images are no longer pinned to IPFS, users can find the IPFS hash of 
            images they have locally. These could be checked against historical blockchain data to come to community consensus on which images were
            actually included in the collection (and what tokenID were they).
          </Typography>
        </AccordionDetails>
      </Accordion>
    </div>
  );
}