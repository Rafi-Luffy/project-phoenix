import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Shield } from "lucide-react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

const sections = [
  {
    title: "Information We Collect",
    content: `We collect information you provide directly to us, such as when you create an account, use our services, or contact us for support.

**Account Information**: When you create a Phoenix account, we collect your name, email address, and password.

**Usage Data**: We automatically collect information about your use of our services, including agent configurations, correction events, and performance metrics.

**Payment Information**: If you subscribe to a paid plan, we collect payment details through our secure payment processor (Stripe).`,
  },
  {
    title: "How We Use Your Information",
    content: `We use the information we collect to:

- Provide, maintain, and improve our services
- Process transactions and send related information
- Send technical notices, updates, and support messages
- Respond to your comments, questions, and customer service requests
- Monitor and analyze trends, usage, and activities
- Detect, investigate, and prevent fraudulent or unauthorized activities`,
  },
  {
    title: "Data Storage and Security",
    content: `We implement appropriate technical and organizational measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.

**Encryption**: All data is encrypted in transit using TLS 1.3 and at rest using AES-256.

**Access Controls**: We maintain strict access controls and audit logs for all data access.

**Data Retention**: We retain your data for as long as your account is active or as needed to provide services.`,
  },
  {
    title: "Sharing of Information",
    content: `We do not sell your personal information. We may share information in the following circumstances:

- With service providers who assist in our operations
- To comply with legal obligations
- To protect our rights, privacy, safety, or property
- In connection with a merger, acquisition, or sale of assets
- With your consent or at your direction`,
  },
  {
    title: "Your Rights and Choices",
    content: `You have the right to:

- Access and receive a copy of your personal data
- Correct inaccurate personal data
- Request deletion of your personal data
- Object to processing of your personal data
- Request restriction of processing
- Data portability

To exercise these rights, contact us at privacy@phoenixruntime.dev`,
  },
  {
    title: "Cookies and Tracking",
    content: `We use cookies and similar technologies to:

- Keep you logged in
- Remember your preferences
- Understand how you use our services
- Improve our services

You can control cookies through your browser settings.`,
  },
  {
    title: "International Data Transfers",
    content: `Your information may be transferred to and processed in countries other than your country of residence. We ensure appropriate safeguards are in place for such transfers, including Standard Contractual Clauses approved by relevant authorities.`,
  },
  {
    title: "Changes to This Policy",
    content: `We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new policy on this page and updating the "Last Updated" date.`,
  },
  {
    title: "Contact Us",
    content: `If you have questions about this Privacy Policy, please contact us at:

**Email**: privacy@phoenixruntime.dev
**Address**: Phoenix Runtime, Inc., 123 AI Boulevard, San Francisco, CA 94105`,
  },
];

export default function Privacy() {
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
                <Shield className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-foreground">Privacy Policy</h1>
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
            className="prose prose-invert max-w-none"
          >
            <p className="text-lg text-muted-foreground mb-12">
              At Phoenix Runtime ("Phoenix", "we", "us", or "our"), we take your privacy seriously. 
              This Privacy Policy explains how we collect, use, disclose, and safeguard your information 
              when you use our services.
            </p>

            <div className="space-y-12">
              {sections.map((section, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.05 }}
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
