import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { WhySection } from "@/components/landing/WhySection";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { ComparisonSection } from "@/components/landing/ComparisonSection";
import { FeaturesGrid } from "@/components/landing/FeaturesGrid";
import { MetricsSection } from "@/components/landing/MetricsSection";
import { FAQ } from "@/components/landing/FAQ";
import { Footer } from "@/components/landing/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <Hero />
        <WhySection />
        <HowItWorks />
        <ComparisonSection />
        <FeaturesGrid />
        <MetricsSection />
        <FAQ />
      </main>
      <Footer />
    </div>
  );
};

export default Index;
