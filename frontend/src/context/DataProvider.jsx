import { createContext, useContext, useState, useEffect } from "react";


const DataContext = createContext();

const DataProvider = ({ children }) => {
  const [data, setData] = useState("cqwen"); 

  return (
    <DataContext.Provider
      value={{
        data,
        setData
      }}
    >
      {children}
    </DataContext.Provider>
  );
};

export const dataState = () => {
  return useContext(DataContext);
};

export default DataProvider;