import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";
import { useAuth, RedirectToSignIn } from "@clerk/clerk-react";
import { useScrollToTop } from "@/hooks/useScrollToTop";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import SignIn from "./pages/SignIn";
import GetStarted from "./pages/GetStarted";
import Pricing from "./pages/Pricing";
import BookOnboarding from "./pages/BookOnboarding";
import Docs from "./pages/Docs";
import GettingStarted from "./pages/GettingStarted";
import ApiReference from "./pages/ApiReference";
import Changelog from "./pages/Changelog";
import Blog from "./pages/Blog";
import Privacy from "./pages/Privacy";
import Terms from "./pages/Terms";
import CoreConcepts from "./pages/docs/CoreConcepts";
import SDKReference from "./pages/docs/SDKReference";
import Examples from "./pages/docs/Examples";
import Guides from "./pages/docs/Guides";
import MultiAgentWorkflows from "./pages/docs/MultiAgentWorkflows";
import ProductionDeployment from "./pages/docs/ProductionDeployment";
import RequestIntegration from "./pages/docs/RequestIntegration";
import BuildCustomIntegration from "./pages/docs/BuildCustomIntegration";
import Integrations from "./pages/docs/Integrations";
import Install from "./pages/docs/Install";
import PythonSDK from "./pages/docs/sdk/PythonSDK";
import JavaScriptSDK from "./pages/docs/sdk/JavaScriptSDK";
import GoSDK from "./pages/docs/sdk/GoSDK";
import CLIDocs from "./pages/docs/sdk/CLIDocs";
import FastAPIIntegration from "./pages/docs/integrations/FastAPIIntegration";
import NextJSIntegration from "./pages/docs/integrations/NextJSIntegration";
import LangChainIntegration from "./pages/docs/integrations/LangChainIntegration";
import VercelIntegration from "./pages/docs/integrations/VercelIntegration";
import DockerIntegration from "./pages/docs/integrations/DockerIntegration";
import KubernetesIntegration from "./pages/docs/integrations/KubernetesIntegration";
import AWSLambdaIntegration from "./pages/docs/integrations/AWSLambdaIntegration";
import CloudflareIntegration from "./pages/docs/integrations/CloudflareIntegration";
import { ConsoleLayout } from "./components/console/ConsoleLayout";
import Dashboard from "./pages/console/Dashboard";
import Agents from "./pages/console/Agents";
import Pipelines from "./pages/console/Pipelines";
import MemoryGraph from "./pages/console/MemoryGraph";
import Experiments from "./pages/console/Experiments";
import Metrics from "./pages/console/Metrics";
import Settings from "./pages/console/Settings";
import Profile from "./pages/console/Profile";
import AgentBuilder from "./pages/console/AgentBuilder";
import Research from "./pages/research/Research";
import SelfRefine from "./pages/research/SelfRefine";
import TreeOfThoughts from "./pages/research/TreeOfThoughts";
import Reflexion from "./pages/research/Reflexion";
import Critic from "./pages/research/Critic";
import ContactSupport from "./pages/docs/ContactSupport";

const queryClient = new QueryClient();

// Protects routes — redirects to Clerk sign-in if not authenticated
const ProtectedRoute = () => {
  const { isSignedIn, isLoaded } = useAuth();
  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="h-8 w-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  if (!isSignedIn) return <RedirectToSignIn />;
  return <Outlet />;
};

const AppContent = () => {
  useScrollToTop();
  
  return (
    <Routes>
        <Route path="/" element={<Index />} />
        <Route path="/signin/*" element={<SignIn />} />
        <Route path="/get-started" element={<GetStarted />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/book-onboarding" element={<BookOnboarding />} />
        <Route path="/docs" element={<Docs />} />
        <Route path="/docs/getting-started" element={<GettingStarted />} />
        <Route path="/docs/api" element={<ApiReference />} />
        <Route path="/docs/concepts" element={<CoreConcepts />} />
        <Route path="/docs/sdk" element={<SDKReference />} />
        <Route path="/docs/sdk/python" element={<PythonSDK />} />
        <Route path="/docs/sdk/javascript" element={<JavaScriptSDK />} />
        <Route path="/docs/sdk/go" element={<GoSDK />} />
        <Route path="/docs/cli" element={<CLIDocs />} />
        <Route path="/docs/install" element={<Install />} />
        <Route path="/docs/examples" element={<Examples />} />
        <Route path="/docs/guides" element={<Guides />} />
        <Route path="/docs/guides/:slug" element={<Guides />} />
        <Route path="/docs/multi-agent" element={<MultiAgentWorkflows />} />
        <Route path="/docs/deployment" element={<ProductionDeployment />} />
        <Route path="/docs/integrations" element={<Integrations />} />
        <Route path="/docs/integrations/request" element={<RequestIntegration />} />
        <Route path="/docs/integrations/custom" element={<BuildCustomIntegration />} />
        <Route path="/docs/support" element={<ContactSupport />} />
        <Route path="/docs/integrations/fastapi" element={<FastAPIIntegration />} />
        <Route path="/docs/integrations/nextjs" element={<NextJSIntegration />} />
        <Route path="/docs/integrations/langchain" element={<LangChainIntegration />} />
        <Route path="/docs/integrations/vercel" element={<VercelIntegration />} />
        <Route path="/docs/integrations/docker" element={<DockerIntegration />} />
        <Route path="/docs/integrations/k8s" element={<KubernetesIntegration />} />
        <Route path="/docs/integrations/lambda" element={<AWSLambdaIntegration />} />
        <Route path="/docs/integrations/cloudflare" element={<CloudflareIntegration />} />
        <Route path="/changelog" element={<Changelog />} />
        <Route path="/blog" element={<Blog />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/terms" element={<Terms />} />
        {/* Research Routes */}
        <Route path="/research" element={<Research />} />
        <Route path="/research/self-refine" element={<SelfRefine />} />
        <Route path="/research/tree-of-thoughts" element={<TreeOfThoughts />} />
        <Route path="/research/reflexion" element={<Reflexion />} />
        <Route path="/research/critic" element={<Critic />} />
        {/* Console Routes — protected by Clerk */}
        <Route element={<ProtectedRoute />}>
        <Route path="/console" element={<ConsoleLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="agents" element={<Agents />} />
          <Route path="builder" element={<AgentBuilder />} />
          <Route path="pipelines" element={<Pipelines />} />
          <Route path="memory" element={<MemoryGraph />} />
          <Route path="experiments" element={<Experiments />} />
          <Route path="metrics" element={<Metrics />} />
          <Route path="settings" element={<Settings />} />
          <Route path="profile" element={<Profile />} />
        </Route>
        </Route>{/* end ProtectedRoute */}
        <Route path="*" element={<NotFound />} />
      </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner position="top-right" richColors />
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
