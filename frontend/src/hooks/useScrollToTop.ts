import { useEffect } from "react";
import { useLocation } from "react-router-dom";

export function useScrollToTop() {
  const { pathname, search } = useLocation();

  useEffect(() => {
    // Check if there's a specific section to scroll to
    const scrollParam = new URLSearchParams(search).get("scroll");
    
    if (scrollParam) {
      // Scroll to the specific section
      const element = document.getElementById(scrollParam);
      if (element) {
        setTimeout(() => {
          element.scrollIntoView({ behavior: "smooth" });
        }, 100);
      }
    } else {
      // Default: scroll to top
      window.scrollTo(0, 0);
    }
  }, [pathname, search]);
}

