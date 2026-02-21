import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  Bot,
  Zap,
  Shield,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Code2,
  Settings,
  Rocket,
  Play,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

interface OnboardingWizardProps {
  open: boolean;
  onClose: () => void;
}

const steps = [
  {
    id: "welcome",
    title: "Welcome to Phoenix",
    description: "Let's set up your first self-healing AI agent in just a few steps.",
    icon: Sparkles,
  },
  {
    id: "agent-type",
    title: "Choose Agent Type",
    description: "Select the type of agent that best fits your use case.",
    icon: Bot,
  },
  {
    id: "configure",
    title: "Configure Your Agent",
    description: "Set up the basic configuration for your agent.",
    icon: Settings,
  },
  {
    id: "connect",
    title: "Connect Your App",
    description: "Integrate Phoenix with your application using our SDK.",
    icon: Code2,
  },
  {
    id: "complete",
    title: "You're All Set!",
    description: "Your agent is ready to start monitoring and self-healing.",
    icon: Rocket,
  },
];

const agentTypes = [
  {
    id: "monitor",
    name: "Monitor Agent",
    description: "Watches for errors and anomalies in real-time",
    icon: Shield,
    color: "text-blue-500",
    bg: "bg-blue-500/10",
  },
  {
    id: "executor",
    name: "Executor Agent",
    description: "Applies automated fixes and patches",
    icon: Zap,
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    id: "critic",
    name: "Critic Agent",
    description: "Validates corrections and ensures quality",
    icon: CheckCircle2,
    color: "text-green-500",
    bg: "bg-green-500/10",
  },
];

export const OnboardingWizard = ({ open, onClose }: OnboardingWizardProps) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedAgentType, setSelectedAgentType] = useState<string | null>(null);
  const [agentName, setAgentName] = useState("");
  const [agentDescription, setAgentDescription] = useState("");

  const handleNext = () => {
    if (currentStep === 1 && !selectedAgentType) {
      toast.error("Please select an agent type");
      return;
    }
    if (currentStep === 2 && !agentName) {
      toast.error("Please enter an agent name");
      return;
    }
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    localStorage.setItem("phoenix_onboarding_complete", "true");
    toast.success("Agent created successfully!");
    onClose();
    navigate("/console/agents");
  };

  const handleSkip = () => {
    localStorage.setItem("phoenix_onboarding_complete", "true");
    onClose();
  };

  if (!open) return null;

  const currentStepData = steps[currentStep];
  const StepIcon = currentStepData.icon;

  return (
    <div className="fixed inset-0 z-[100] bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl bg-card border border-border rounded-2xl shadow-2xl overflow-hidden"
      >
        {/* Header */}
        <div className="p-6 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <StepIcon className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">{currentStepData.title}</h2>
              <p className="text-sm text-muted-foreground">{currentStepData.description}</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={handleSkip}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Progress */}
        <div className="px-6 pt-4">
          <div className="flex gap-2">
            {steps.map((step, i) => (
              <div
                key={step.id}
                className={`h-1.5 flex-1 rounded-full transition-colors ${
                  i <= currentStep ? "bg-primary" : "bg-muted"
                }`}
              />
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Step {currentStep + 1} of {steps.length}
          </p>
        </div>

        {/* Content */}
        <div className="p-6 min-h-[300px]">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {currentStep === 0 && (
                <div className="text-center py-8">
                  <div className="h-24 w-24 mx-auto rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center mb-6">
                    <Sparkles className="h-12 w-12 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Create Your First Agent</h3>
                  <p className="text-muted-foreground max-w-md mx-auto">
                    Phoenix agents continuously monitor your application, detect errors, 
                    and automatically apply fixes in real-time. Let's get you started!
                  </p>
                  <div className="flex justify-center gap-4 mt-8">
                    {[
                      { icon: Shield, label: "Monitor" },
                      { icon: Zap, label: "Detect" },
                      { icon: CheckCircle2, label: "Heal" },
                    ].map((item, i) => (
                      <div key={i} className="flex flex-col items-center gap-2">
                        <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
                          <item.icon className="h-6 w-6 text-primary" />
                        </div>
                        <span className="text-sm font-medium">{item.label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {currentStep === 1 && (
                <div className="space-y-4">
                  {agentTypes.map((type) => (
                    <Card
                      key={type.id}
                      className={`cursor-pointer transition-all ${
                        selectedAgentType === type.id
                          ? "border-primary bg-primary/5"
                          : "border-border hover:border-primary/50"
                      }`}
                      onClick={() => setSelectedAgentType(type.id)}
                    >
                      <CardContent className="p-4 flex items-center gap-4">
                        <div className={`h-12 w-12 rounded-xl ${type.bg} flex items-center justify-center`}>
                          <type.icon className={`h-6 w-6 ${type.color}`} />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold">{type.name}</h4>
                          <p className="text-sm text-muted-foreground">{type.description}</p>
                        </div>
                        {selectedAgentType === type.id && (
                          <CheckCircle2 className="h-5 w-5 text-primary" />
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {currentStep === 2 && (
                <div className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="agent-name">Agent Name</Label>
                    <Input
                      id="agent-name"
                      placeholder="e.g., Production Monitor"
                      value={agentName}
                      onChange={(e) => setAgentName(e.target.value)}
                      className="bg-background"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="agent-desc">Description (optional)</Label>
                    <Input
                      id="agent-desc"
                      placeholder="What will this agent monitor?"
                      value={agentDescription}
                      onChange={(e) => setAgentDescription(e.target.value)}
                      className="bg-background"
                    />
                  </div>
                  <Card className="bg-muted/30 border-dashed">
                    <CardContent className="p-4">
                      <h4 className="font-medium mb-2">Selected Configuration</h4>
                      <div className="flex flex-wrap gap-2">
                        <Badge variant="outline">
                          {agentTypes.find(t => t.id === selectedAgentType)?.name}
                        </Badge>
                        <Badge variant="outline">Auto-healing enabled</Badge>
                        <Badge variant="outline">Real-time monitoring</Badge>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {currentStep === 3 && (
                <div className="space-y-6">
                  <p className="text-muted-foreground">
                    Install the Phoenix SDK and initialize it in your application:
                  </p>
                  <div className="space-y-4">
                    <div className="bg-muted/50 rounded-lg p-4 font-mono text-sm overflow-x-auto">
                      <p className="text-muted-foreground"># Install the SDK</p>
                      <p className="text-primary">pip install phoenix-ai</p>
                    </div>
                    <div className="bg-muted/50 rounded-lg p-4 font-mono text-sm overflow-x-auto">
                      <p className="text-muted-foreground"># Initialize in your code</p>
                      <p><span className="text-blue-400">from</span> phoenix <span className="text-blue-400">import</span> Phoenix</p>
                      <p className="mt-2">phoenix = Phoenix(</p>
                      <p className="pl-4">api_key=<span className="text-green-400">"your_api_key"</span>,</p>
                      <p className="pl-4">agent=<span className="text-green-400">"{agentName || 'my-agent'}"</span></p>
                      <p>)</p>
                      <p className="mt-2">phoenix.start()</p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    You can also copy your API key from the Settings page after completing setup.
                  </p>
                </div>
              )}

              {currentStep === 4 && (
                <div className="text-center py-8">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", duration: 0.5 }}
                    className="h-24 w-24 mx-auto rounded-full bg-gradient-to-br from-green-500/20 to-primary/20 flex items-center justify-center mb-6"
                  >
                    <CheckCircle2 className="h-12 w-12 text-green-500" />
                  </motion.div>
                  <h3 className="text-xl font-semibold mb-2">Agent Created Successfully!</h3>
                  <p className="text-muted-foreground max-w-md mx-auto mb-6">
                    Your {agentName || "new agent"} is now ready to start monitoring your application 
                    and applying self-healing fixes.
                  </p>
                  <div className="flex justify-center gap-4">
                    <Card className="bg-muted/30 p-4 text-center">
                      <p className="text-2xl font-bold text-primary">24/7</p>
                      <p className="text-xs text-muted-foreground">Monitoring</p>
                    </Card>
                    <Card className="bg-muted/30 p-4 text-center">
                      <p className="text-2xl font-bold text-primary">&lt;5s</p>
                      <p className="text-xs text-muted-foreground">Response Time</p>
                    </Card>
                    <Card className="bg-muted/30 p-4 text-center">
                      <p className="text-2xl font-bold text-primary">99%</p>
                      <p className="text-xs text-muted-foreground">Success Rate</p>
                    </Card>
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-border flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={handleBack}
            disabled={currentStep === 0}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="flex gap-3">
            {currentStep < steps.length - 1 ? (
              <>
                <Button variant="ghost" onClick={handleSkip}>
                  Skip for now
                </Button>
                <Button onClick={handleNext} className="bg-primary hover:bg-primary/90">
                  Continue
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </>
            ) : (
              <Button onClick={handleComplete} className="bg-primary hover:bg-primary/90">
                <Play className="h-4 w-4 mr-2" />
                Go to Dashboard
              </Button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
};
