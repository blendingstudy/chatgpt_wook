module.exports = (sequelize, DataTypes) => {
  const Post = sequelize.define('Post', {
    title: DataTypes.STRING,
    content: DataTypes.TEXT,
    author: DataTypes.STRING,
    createdAt: DataTypes.DATE
  }, {});
  Post.associate = function(models) {
    // associations can be defined here
  };
  return Post;
};