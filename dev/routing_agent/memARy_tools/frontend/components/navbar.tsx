import Link from 'next/link';

export default function Navbar() {
  
  const linkStyles = "mx-4";
  
  return (
    <div className="absolute bottom-0 w-[100%]">
      <nav className="bg-gray-800 p-4 text-white">
        {/* Your navigation links go here */}
        <div className="flex xxs:justify-evenly lg:justify-normal">
          <Link className={linkStyles} href="/">Home</Link>
          <Link className={linkStyles} href="/camera">Camera</Link>
          {/* <Link className={linkStyles} href="/">Logs</Link> */}
        </div>
      </nav>
    </div>
  );
}