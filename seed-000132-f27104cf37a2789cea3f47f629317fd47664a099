"""Policy Intelligence Engine — retrieval + synthesis over the municipal policy corpus.

V1 is deliberately embedding-free: page-anchored chunks in Postgres, pure-Python
lexical retrieval, one Claude synthesis call with mechanically-verified citations.
pgvector is a later upgrade behind the same retrieve() seam (only worth it when
the corpus outgrows ~30 documents).
"""
