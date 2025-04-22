"use client"

import {useEffect, useState} from "react";

interface User {
  score: number,
  name: string
} // Testing 

export default function Home() {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    async function getPlacements() {
      const response = await fetch("https://adsc-competition-website.onrender.com/placements", {
        method: "GET",
        headers: {
          'Access-Control-Allow-Origin': '*'
        },
      });
      const data = await response.json();
      setUsers(data['Placements']);
    }
    getPlacements() 
    setInterval(getPlacements, 1000 * 10) // every 10 seconds for testing
  }, [])

  const columns = ["Rank", "Username", "Score"];
  
  const styleOne = "bg-color-"

  return (
    <div className="p-8">
      <h1 className="text-3xl">Leaderboard</h1>
      <div className="grid grid-cols-3 py-4">
        {
          columns.map((column, index) => (
            <div className="text-xl" key={index}>
              {column}
            </div>
          ))
        }
        {
          users.map((user, index) => (
            <>
              <h1>{index+1}</h1>
              <h1>{user.name}</h1>
              <h1>{user.score}</h1>
            </>
          ))
        }
      </div>
    </div>
  );
}
