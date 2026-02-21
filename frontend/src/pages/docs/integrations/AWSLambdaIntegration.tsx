import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Zap, Cloud, Lock, Timer } from "lucide-react";
import { useState } from "react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={copy}
      className="p-2 rounded-lg hover:bg-muted/50 transition-colors text-muted-foreground hover:text-foreground"
    >
      {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
    </button>
  );
}

const AWSLogo = () => (
  <svg viewBox="0 0 24 24" className="w-16 h-16 text-[#FF9900]">
    <text x="4" y="18" fontSize="18" fontWeight="bold" fill="currentColor">λ</text>
  </svg>
);

const features = [
  {
    icon: Zap,
    title: "Serverless Agents",
    description: "Pay only for what you use with automatic scaling"
  },
  {
    icon: Cloud,
    title: "AWS Integration",
    description: "Native integration with S3, DynamoDB, and more"
  },
  {
    icon: Lock,
    title: "IAM Security",
    description: "Fine-grained access control with IAM roles"
  },
  {
    icon: Timer,
    title: "Warm Starts",
    description: "Optimized for minimal cold start latency"
  }
];

const handlerExample = `import json
import os
from phoenix import Agent, Phoenix

# Initialize outside handler for connection reuse
phoenix = Phoenix(api_key=os.environ['PHOENIX_API_KEY'])

agent = Agent(
    name='lambda-agent',
    model='gpt-4',
    self_healing=True,
    config={
        'max_retries': 3,
        'timeout': 25  # Leave 5s buffer for Lambda
    }
)

def lambda_handler(event, context):
    """
    AWS Lambda handler for Phoenix agent execution.
    """
    try:
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '')
        
        if not message:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Message required'})
            }
        
        # Run agent with context
        result = agent.run(
            message,
            context={
                'request_id': context.aws_request_id,
                'function_name': context.function_name
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'X-Corrections-Count': str(result.corrections_count)
            },
            'body': json.dumps({
                'response': result.content,
                'corrections': result.corrections_count,
                'confidence': result.confidence,
                'latency_ms': result.latency_ms
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }`;

const samTemplateExample = `AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Phoenix Agent Lambda Function

Globals:
  Function:
    Timeout: 30
    MemorySize: 1024
    Runtime: python3.11
    Architectures:
      - arm64
    Environment:
      Variables:
        PHOENIX_API_KEY: !Ref PhoenixApiKey

Parameters:
  PhoenixApiKey:
    Type: String
    NoEcho: true
    Description: Phoenix API Key

Resources:
  PhoenixAgentFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: handler.lambda_handler
      Description: Self-healing AI agent powered by Phoenix
      Events:
        Api:
          Type: Api
          Properties:
            Path: /agent
            Method: post
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref AgentMemoryTable
        - S3ReadPolicy:
            BucketName: !Ref AgentAssetsBucket

  AgentMemoryTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: phoenix-agent-memory
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE

  AgentAssetsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub phoenix-assets-\${AWS::AccountId}

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub https://\${ServerlessRestApi}.execute-api.\${AWS::Region}.amazonaws.com/Prod/agent`;

const streamingExample = `import json
from phoenix import Agent

def lambda_handler(event, context):
    """
    Lambda handler with response streaming for Phoenix agents.
    Requires Lambda response streaming enabled.
    """
    message = json.loads(event['body']).get('message', '')
    
    agent = Agent(
        name='stream-agent',
        model='gpt-4',
        self_healing=True
    )

    def generate():
        for chunk in agent.stream(message):
            yield json.dumps({
                'content': chunk.content,
                'done': chunk.done,
                'correction': chunk.correction_applied
            }) + '\\n'

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/x-ndjson',
            'Transfer-Encoding': 'chunked'
        },
        'body': generate(),
        'isBase64Encoded': False
    }`;

const deployCommandsExample = `# Install SAM CLI
pip install aws-sam-cli

# Build the Lambda package
sam build

# Deploy to AWS
sam deploy --guided \\
  --stack-name phoenix-agent \\
  --parameter-overrides PhoenixApiKey=$PHOENIX_API_KEY

# Test locally
sam local invoke PhoenixAgentFunction \\
  --event events/test.json

# View logs
sam logs --stack-name phoenix-agent --tail`;

const layerExample = `# Create Phoenix Lambda Layer for faster deployments

# 1. Create layer directory
mkdir -p phoenix-layer/python

# 2. Install Phoenix
pip install phoenix-ai -t phoenix-layer/python

# 3. Package layer
cd phoenix-layer
zip -r phoenix-layer.zip python

# 4. Publish layer
aws lambda publish-layer-version \\
  --layer-name phoenix-ai \\
  --zip-file fileb://phoenix-layer.zip \\
  --compatible-runtimes python3.11 \\
  --compatible-architectures arm64 x86_64`;

export default function AWSLambdaIntegration() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(255,153,0,0.15),transparent_60%)]" />
        
        <div className="container mx-auto max-w-5xl relative z-10">
          <Link 
            to="/docs/sdk"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to SDK Reference
          </Link>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex items-center gap-6 mb-6"
          >
            <AWSLogo />
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                AWS Lambda Integration
              </h1>
              <p className="text-lg text-muted-foreground mt-2">
                Deploy serverless Phoenix agents on AWS Lambda
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-4 rounded-xl bg-muted/20 border border-border"
              >
                <feature.icon className="w-8 h-8 text-[#FF9900] mb-3" />
                <h3 className="font-semibold text-foreground mb-1">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Handler */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Lambda Handler</h2>
          <p className="text-muted-foreground mb-6">
            Optimized Lambda handler with connection reuse and error handling.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">handler.py</span>
              <CopyButton text={handlerExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{handlerExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* SAM Template */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">SAM Template</h2>
          <p className="text-muted-foreground mb-6">
            Complete AWS SAM template with API Gateway, DynamoDB, and S3.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">template.yaml</span>
              <CopyButton text={samTemplateExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{samTemplateExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Streaming */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Response Streaming</h2>
          <p className="text-muted-foreground mb-6">
            Stream agent responses using Lambda response streaming.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">streaming_handler.py</span>
              <CopyButton text={streamingExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{streamingExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Layer */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Lambda Layer</h2>
          <p className="text-muted-foreground mb-6">
            Create a Lambda layer for faster cold starts and shared dependencies.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">create-layer.sh</span>
              <CopyButton text={layerExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{layerExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Deploy */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Deploy Commands</h2>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">Terminal</span>
              <CopyButton text={deployCommandsExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{deployCommandsExample}</code>
            </pre>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
