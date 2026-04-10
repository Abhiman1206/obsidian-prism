"use client";

import React from "react";
import { motion } from "framer-motion";

type FloatingPrismProps = {
  className?: string;
};

export function FloatingPrism({ className }: FloatingPrismProps) {
  return (
    <motion.div
      className={className ?? "floating-prism"}
      aria-hidden="true"
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      whileHover={{ scale: 1.03 }}
    >
      <motion.div
        className="floating-prism__body"
        animate={{ y: [0, -8, 0], rotate: [-3, 3, -3] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
      >
        <svg viewBox="0 0 64 64" role="img" focusable="false">
          <path d="M32 4L53 18L59 44L35 60L10 46L6 33L15 19Z" fill="#f5f5f5" stroke="#050505" strokeWidth="4" strokeLinejoin="round" />
          <path d="M32 4L15 19L6 33L10 46L35 60Z" fill="#050505" />
          <path d="M22 21L17 31L26 26Z" fill="#f5f5f5" />
          <path d="M41 23L49 28" stroke="#050505" strokeWidth="3" strokeLinecap="round" />
          <path d="M44 26L51 31" stroke="#050505" strokeWidth="3" strokeLinecap="round" />
          <path d="M45 45L48 43" stroke="#050505" strokeWidth="3" strokeLinecap="round" />
          <path d="M40 31L44 35L41 40L36 41L34 36L36 31Z" fill="#050505" />
          <path d="M38 34L38 38L41 36Z" fill="#f5f5f5" />
        </svg>
      </motion.div>
    </motion.div>
  );
}
