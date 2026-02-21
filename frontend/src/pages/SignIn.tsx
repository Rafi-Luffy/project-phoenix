import { SignIn as ClerkSignIn } from "@clerk/clerk-react";
import { PhoenixLogo } from "@/components/landing/PhoenixLogo";
import { Link } from "react-router-dom";

export default function SignIn() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center px-4">
      {/* Logo */}
      <Link to="/" className="flex items-center gap-3 mb-8 group">
        <PhoenixLogo size="md" animated />
        <span className="font-bold text-2xl tracking-tight text-foreground">Phoenix</span>
      </Link>

      {/* Clerk hosted SignIn UI — styled to match dark theme */}
      <ClerkSignIn
        routing="path"
        path="/signin"
        afterSignInUrl="/console"
        afterSignUpUrl="/console"
        appearance={{
          variables: {
            colorPrimary: "hsl(267, 84%, 67%)",
            colorBackground: "hsl(240, 10%, 5%)",
            colorText: "hsl(0, 0%, 95%)",
            colorInputBackground: "hsl(240, 6%, 10%)",
            colorInputText: "hsl(0, 0%, 95%)",
            colorNeutral: "hsl(240, 5%, 65%)",
            borderRadius: "0.75rem",
          },
          elements: {
            card: "bg-card border border-border shadow-2xl",
            headerTitle: "text-foreground font-bold",
            headerSubtitle: "text-muted-foreground",
            socialButtonsBlockButton:
              "border border-border bg-muted hover:bg-muted/80 text-foreground",
            formButtonPrimary:
              "bg-primary hover:bg-primary/90 text-primary-foreground",
            formFieldInput:
              "bg-muted border-border text-foreground placeholder:text-muted-foreground",
            footerActionLink: "text-primary hover:text-primary/80",
          },
        }}
      />

      <p className="mt-6 text-sm text-muted-foreground">
        Back to{" "}
        <Link to="/" className="text-primary hover:underline">
          home
        </Link>
      </p>
    </div>
  );
}
