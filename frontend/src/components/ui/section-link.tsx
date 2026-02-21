import { useLocation, useNavigate } from "react-router-dom";

interface SectionLinkProps {
  href: string;
  children: React.ReactNode;
  className?: string;
}

export function SectionLink({ href, children, className }: SectionLinkProps) {
  const location = useLocation();
  const navigate = useNavigate();

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();

    const isHomePage = location.pathname === "/";
    const sectionId = href.split("#")[1];

    if (isHomePage && sectionId) {
      // On home page - smooth scroll to section
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: "smooth" });
      }
    } else if (sectionId) {
      // On another page - navigate to home and scroll to section
      navigate("/?scroll=" + sectionId);
      // The scroll will be handled by the useEffect in App
    } else {
      // No section ID, just navigate
      navigate(href);
    }
  };

  return (
    <a href={href} onClick={handleClick} className={className}>
      {children}
    </a>
  );
}
