import { createBrowserRouter } from "react-router";
import { Home } from "./pages/Home";
import { VideoPlayer } from "./pages/VideoPlayer";
import { SavedVideos } from "./pages/SavedVideos";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Home,
  },
  {
    path: "/video/:id",
    Component: VideoPlayer,
  },
  {
    path: "/saved",
    Component: SavedVideos,
  },
]);