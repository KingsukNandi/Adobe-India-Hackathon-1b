import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Upload from "./components/Upload";
import Analyst from "./components/Analyst";
import Home from "./components/Home";

function App() {
  return (
    <BrowserRouter>
      {/*<nav className="flex gap-4 p-4 justify-end">
        <Link to="/upload" className="btn btn-primary">
          Upload
        </Link>
        <Link to="/analyst" className="btn btn-secondary">
          Analyst
        </Link>
      </nav>*/}
      <Routes>
        <Route path="/upload" element={<Upload />} />
        <Route path="/analyst" element={<Analyst />} />
        <Route path="*" element={<Upload />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
