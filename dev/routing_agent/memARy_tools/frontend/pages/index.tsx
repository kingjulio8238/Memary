import { Inter } from 'next/font/google'
import Navbar from '@/components/navbar'
import { useRef, useState } from 'react';

//@ts-ignore

const inter = Inter({ subsets: ['latin'] });

export default function Home() {
  return (
    <main className="flex flex-col lg:justify-between items-center h-[50rem]">
      <h1>
        home page
      </h1>
    </main>
  )
}
