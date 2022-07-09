import styles from '../styles/Home.module.css'
import Image from 'next/image'
import TwitterIcon from '@mui/icons-material/Twitter';
import GitHubIcon from '@mui/icons-material/GitHub';

export default function Footer() {
  return (
    <footer className={styles.footer} style={{}}>
      {/* <a
        href="https://vercel.com?utm_source=create-next-app&utm_medium=default-template&utm_campaign=create-next-app"
        target="_blank"
        rel="noopener noreferrer"
      >
        Powered by{' '}
        <span className={styles.logo}>
          <Image src="/vercel.svg" alt="Vercel Logo" width={72} height={16} />
        </span>
      </a> */}
      <GitHubIcon onClick={() => window.location.href="https://github.com/verumlotus/NFT-Batch-Download"} />
      <TwitterIcon onClick={() => window.location.href="https://twitter.com/verumlotus"} />
    </footer>
  )
}