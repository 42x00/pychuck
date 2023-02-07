import os

dataset_root = '/Users/ykli/research/music356/data/genre/genres_original'

for genre in os.listdir(dataset_root):
    genre_dir = os.path.join(dataset_root, genre)
    for song in os.listdir(genre_dir):
        song_path = os.path.join(genre_dir, song)
        y, sr = librosa.load(song_path)
        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        print(mfcc.shape)
