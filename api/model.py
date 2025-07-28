from sentence_transformers import SentenceTransformer
model = SentenceTransformer("intfloat/multilingual-e5-small")
model.save("localmodel")
