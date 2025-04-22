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
  
  const styleOne = "bg-white even:bg-gray-100"
  const styleTwo = "bg-white even:bg-gray-100"
  const defaultStyle = "px-4 py-2 flex justify-between items-center text-center border-l-4 "

  const firstPlace = "bg-yellow-100 border-yellow-400 font-semibold text-yellow-700"
  const secondPlace = "bg-gray-100 border-gray-400 font-semibold text-gray-700"
  const thirdPlace = "bg-orange-100 border-orange-400 text-orange-700"

  const determineStyle = (index: number) => {
    if(index == 0) {
      return defaultStyle + firstPlace
    }
    else if(index == 1) {
      return defaultStyle + secondPlace
    }
    else if(index == 2) {
      return defaultStyle + thirdPlace
    }
    else if(index % 2 == 0) {
      return defaultStyle + styleOne
    } else {
      return defaultStyle + styleTwo
    }
  }

  return (
    <div className="p-8">
      <div className="text-3xl m-auto text-center font-semibold text-gray-800 mb-2">Leaderboard</div>
      <div className="w-1/2 m-auto py-4">
        <div className="px-4 py-2 flex justify-between items-center text-center border-b border-gray-200 mb-2 uppercase ont-medium text-gray-500">
          {
            columns.map((column, index) => (
              <div key={index}>
                {column}
              </div>
            ))
          }
        </div>
        {
          users.map((user, index) => (
            <div key={index} className={determineStyle(index)}>
              <h1>{index+1}</h1>
              <h1>{user.name}</h1>
              <h1>{user.score}</h1>
            </div>
          ))
        }
      </div>
    </div>
  );
}
