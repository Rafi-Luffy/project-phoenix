import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, FileText } from "lucide-react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const sections = [
  {
    title: "1. Acceptance of Terms",
    content: `By accessing or using Phoenix Runtime's services, you agree to be bound by these Terms of Service and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using or accessing our services.`,
  },
  {
    title: "2. Description of Service",
    content: `Phoenix Runtime provides an autonomous, self-healing agent framework for runtime self-correction. Our services include:

- Agent creation and deployment platform
- Self-correction and self-healing capabilities
- Memory management systems
- Multi-agent orchestration tools
- Monitoring and analytics dashboards
- API access and SDK libraries

We reserve the right to modify, suspend, or discontinue any part of the service at any time.`,
  },
  {
    title: "3. Account Registration",
    content: `To use our services, you must:

- Provide accurate and complete registration information
- Maintain the security of your account credentials
- Promptly update any changes to your information
- Accept responsibility for all activities under your account

You must be at least 18 years old to create an account. Organizations must ensure authorized representatives create accounts.`,
  },
  {
    title: "4. Acceptable Use",
    content: `You agree not to use our services to:

- Violate any laws or regulations
- Infringe on intellectual property rights
- Transmit malware or malicious code
- Attempt to gain unauthorized access to our systems
- Interfere with other users' access to the service
- Use the service for any harmful or illegal purpose
- Resell or redistribute our services without permission

We may suspend or terminate accounts that violate these policies.`,
  },
  {
    title: "5. Intellectual Property",
    content: `**Our Property**: Phoenix Runtime and its original content, features, and functionality are owned by Phoenix Runtime, Inc. and are protected by international copyright, trademark, and other intellectual property laws.

**Your Content**: You retain ownership of content you create using our services. By using our services, you grant us a license to host, store, and display your content as necessary to provide the service.

**Feedback**: Any feedback or suggestions you provide may be used by us without obligation to you.`,
  },
  {
    title: "6. Payment Terms",
    content: `**Billing**: Paid plans are billed in advance on a monthly or annual basis. All fees are non-refundable except as required by law.

**Price Changes**: We may change our prices with 30 days notice. Continued use after price changes constitutes acceptance.

**Taxes**: You are responsible for all applicable taxes. We will add taxes where required by law.

**Failed Payments**: If payment fails, we may suspend access until payment is resolved.`,
  },
  {
    title: "7. Service Level Agreement",
    content: `For paid plans, we commit to:

- 99.9% uptime for the core platform
- 24-hour response time for critical issues
- Regular security updates and patches

Enterprise customers may negotiate custom SLAs. Uptime guarantees exclude scheduled maintenance and force majeure events.`,
  },
  {
    title: "8. Limitation of Liability",
    content: `TO THE MAXIMUM EXTENT PERMITTED BY LAW:

- Phoenix Runtime shall not be liable for any indirect, incidental, special, consequential, or punitive damages
- Our total liability shall not exceed the amount paid by you in the 12 months preceding the claim
- We are not liable for any loss of data, profits, or business opportunities

These limitations apply regardless of the theory of liability.`,
  },
  {
    title: "9. Indemnification",
    content: `You agree to indemnify and hold harmless Phoenix Runtime, its officers, directors, employees, and agents from any claims, damages, losses, or expenses arising from:

- Your use of our services
- Your violation of these terms
- Your violation of any third-party rights
- Content you submit or transmit through our services`,
  },
  {
    title: "10. Termination",
    content: `We may terminate or suspend your account immediately, without prior notice, for:

- Breach of these Terms
- Non-payment of fees
- Suspected fraudulent or illegal activity

Upon termination, your right to use the service ceases immediately. We may retain certain data as required by law or for legitimate business purposes.`,
  },
  {
    title: "11. Governing Law",
    content: `These Terms shall be governed by and construed in accordance with the laws of the State of California, without regard to its conflict of law provisions. Any disputes shall be resolved in the courts of San Francisco County, California.`,
  },
  {
    title: "12. Changes to Terms",
    content: `We reserve the right to modify these terms at any time. We will provide notice of material changes by:

- Posting the updated terms on our website
- Sending an email to registered users

Continued use after changes constitutes acceptance of the modified terms.`,
  },
  {
    title: "13. Contact Information",
    content: `For questions about these Terms of Service, please contact us at:

**Email**: legal@phoenixruntime.dev
**Address**: Phoenix Runtime, Inc., 123 AI Boulevard, San Francisco, CA 94105`,
  },
];

export default function Terms() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Link
              to="/"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors mb-6"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Link>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                <FileText className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-foreground">Terms of Service</h1>
              </div>
            </div>

            <p className="text-muted-foreground">
              Last updated: December 28, 2024
            </p>
          </motion.div>
        </div>
      </section>

      {/* Content */}
      <section className="pb-24 px-4">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <p className="text-lg text-muted-foreground mb-12">
              Please read these Terms of Service ("Terms") carefully before using Phoenix Runtime's 
              services. These Terms constitute a legally binding agreement between you and Phoenix Runtime, Inc.
            </p>

            <div className="space-y-10">
              {sections.map((section, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.03 }}
                >
                  <h2 className="text-xl font-bold text-foreground mb-4">{section.title}</h2>
                  <div className="text-muted-foreground whitespace-pre-line">
                    {section.content}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
